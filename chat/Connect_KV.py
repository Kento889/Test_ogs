
import logging
import socket
from tkinter import messagebox
from chat.ReadExcel import type_dev
from chat.ReadExcel import start_dev
from chat.ReadExcel import end_dev
from chat.ReadExcel import fuc_count
from chat.ReadExcel import p_2d_all
from chat.ReadExcel import AL_2d_all
from chat.ReadExcel import AL_rcount
from chat.ReadExcel import AL_ccount
from chat.ReadExcel import P_list
from chat.ReadExcel import PP_list
from chat.ReadExcel import line_len
from chat.ReadExcel import walk_speed
from chat.ReadExcel import F_list
from chat.ReadExcel import S_comment
from chat.ReadExcel import A_comment
from chat.ReadExcel import B_comment
from chat.ReadExcel import C_comment
import tkinter
from tkinter import ttk
import datetime
import math
import numpy as np
from itertools import product
import copy
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio



logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')
host_ip = "192.168.0.110"   # PLCのIPアドレス 
host_port = 8501           # 上位リンク通信のポート番号(デフォルト値)
 
logging.debug('start')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket.AF_INETでip4を使うことを指定。socket.SOCK_STREAMでTCPを使うことを指定。
 
try:
        #クライアント接続
        client.connect((host_ip,host_port))    # サーバーに接続(kv-7500にTCP接続/上位リンク通信)
        connectflag = 11
except:
        print("PLC接続NG")

NowAL = []
MemoryAL = []
for i in range(end_dev - start_dev + 1):
    MemoryAL.append("0000000000000000")

PLCsend = [] #PLC送信用
tempLev = [] #PLC送信用信号の異常レベル格納
tempFp = [] #PLC送信用信号の設備優先度格納
BPLCsend = [] #PLC送信用１個前履歴
Websend = [] #Webアプリ送信用
Webfac = [] #Webアプリ送信用設備名
Webalarm = [] #Webアプリ送信用アラーム内容
se_count = 10
for s in range(se_count):
    PLCsend.append("0")
    tempLev.append("0")
    tempFp.append(0)
    BPLCsend.append("0")
    Websend.append(" ")
    Webfac.append(" ")
    Webalarm.append(" ")
    
st = 10 #同一設備　アラーム複数発生数

#二次元配列
#AL=[[優先1設備,2,3,4,5,6,・・・・・],[1,2,3,・・・・]・・・・・・[1,2,3・・・]]
for pn in range(st):
    code = 'ALdev2d = {}'.format((pn+1)*[fuc_count *["e"]])    
    exec(code)
    code = 'ALbit2d = {}'.format((pn+1)*[fuc_count *[0]])
    exec(code)
    code = 'ALlev2d = {}'.format((pn+1)*[fuc_count *["e"]])
    exec(code)
    code = 'ALtime2d = {}'.format((pn+1)*[fuc_count *[0]])
    exec(code)
    code = 'ALcont2d = {}'.format((pn+1)*[fuc_count *["e"]])
    exec(code)
    code = 'starttime2d = {}'.format((pn+1)*[fuc_count *["e"]])
    exec(code)
    code = 'elapsedtime2d = {}'.format((pn+1)*[fuc_count *[0]])
    exec(code)
    code = 'remaintime2d = {}'.format((pn+1)*[fuc_count *[0]])
    exec(code)

#PLC送信配列関連へ格納
def DataInsert(number, level, priority ):
    BPLCsend.clear()
    for rs in range(len(PLCsend)):
        BPLCsend.insert(rs, PLCsend[rs])
    #BPLCsend = copy.copy(PLCsend)
    PLCsend.insert(number, level + str(priority))
    tempLev.insert(number, level)
    tempFp.insert(number,priority)   
    if level == "S":
        sd_comment = S_comment
    elif level == "A":
        sd_comment = A_comment
    elif level == "B":
        sd_comment = B_comment
    elif level == "C":
        sd_comment = C_comment
    Websend.insert(number, F_list[priority] + " " + sd_comment)
    Webfac.insert(number, F_list[priority])
    Webalarm.insert(number, sd_comment)


#アラーム計算
def Alarm(level, level1, level2, level3, TR, PC):            
    for x in range(se_count):
        #自レベルのみが既に格納されている時    
        if level in tempLev and\
           level1 not in tempLev and\
           level2 not in tempLev and\
           level3 not in tempLev: 
            #既存自レベルより優先度高い同レベル発生時 
            if PC < tempFp[x]  and level + str(PC) not in PLCsend and tempLev[x] == level:                                  
                k = 0
                while tempLev[x+k] == level and PC < tempFp[x+k]:
                    pick = []
                    picktime =[]
                    for i in range(se_count): #自レベル残り時間最大値を抽出
                        if ALlev2d[i][tempFp[x+k]] == level:
                            pick.append(i)                        
                            picktime.append(remaintime2d[i][tempFp[x+k]])                                
                    culremaintime = max(picktime) #自レベル残り時間最大値
                                
                    targetPos = PP_list[tempFp[x+k]] #計算対象の設備座標
                    subjectPos = PP_list[PC] #異常発生設備の設備座標
                    movetime = abs(targetPos - subjectPos) * 0.01 * line_len / walk_speed #移動時間
                            
                    #優先度低⇒優先度高の順で発生　⇒　優先度高に格納する条件
                    if culremaintime  > ALtime2d[TR][PC] + movetime * 2:
                        DataInsert(x+k, level, PC)                                  
                        break
                    else:
                        k = k+1
                        DataInsert(x+k, level, PC)
                        break
                else:
                    if tempLev[x+k] != level:
                        DataInsert(x+k, level, PC)
                        break
            #既存レベルより優先度低い同レベル発生時                                                                                   
            if PC > tempFp[x]  and level + str(PC) not in PLCsend and tempLev[x] == level:      
                for c in range(se_count):
                    if tempLev[c] == level and PC < tempFp[c]:
                        DataInsert(c, level, PC)                                    
                        break
                    if tempLev[c] == level and (tempFp[c] < PC and PC < tempFp[c+1] or tempLev[c+1] != level):       
                        DataInsert(c+1, level, PC)                                  
                        break               
                else:
                    continue
                break                    
        else:        
            if level + str(PC) not in PLCsend:
                #自レベル以外の自レベル以上のみが既に格納されている時
                if (level1 in tempLev or level2 in tempLev or level3 in tempLev) and level not in tempLev:                   
                    for c in range(se_count):
                        if tempLev[c] != level1 and tempLev[c] != level2 and tempLev[c] != level3:                              
                            DataInsert(c, level, PC)
                            break 
                #自レベル以外の自レベル以上と自レベルが既に格納されている時
                elif (level1 in tempLev or level2 in tempLev or level3 in tempLev) and level in tempLev: 
                    for c in range(se_count):
                        if tempLev[c] == level and PC < tempFp[c]:                              
                            DataInsert(c, level, PC)
                            break    
                        if tempLev[c] == level and (tempFp[c] < PC and PC < tempFp[c+1] or tempLev[c+1] != level):       
                            DataInsert(c+1, level, PC)                                  
                            break               
                else:
                    DataInsert(x, level, PC)
                break

def event_triger():   
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'event_sharif',
        {
            'type': 'chat_message',
            'message1': Webfac[0],
            'message2': Webfac[1],
            'message3': Webfac[2],
            'message4': Webfac[3],
            'message5': Webfac[4],
            'message6': Webfac[5],
            'message7': Webfac[6],
            'message8': Webfac[7],
            'message9': Webfac[8],
            'message10': Webfac[9],
            'message11': Webalarm[0],
            'message12': Webalarm[1],
            'message13': Webalarm[2],
            'message14': Webalarm[3],
            'message15': Webalarm[4],
            'message16': Webalarm[5],
            'message17': Webalarm[6],
            'message18': Webalarm[7],
            'message19': Webalarm[8],
            'message20': Webalarm[9],
        }
    ) 

def main1(): 
    updateflag = 1
    while updateflag == 1:  
        c = 0
        NowAL = []
    
        for dev_No in range(start_dev , end_dev + 1):       
            comand = "RD " +  str(type_dev) + str(dev_No) + "\r"        # 上位リンク通信のコマンド（データ読み出しコマンド）
            #comand = "RDS DM53000.D 2\r"    # 上位リンク通信のコマンド（データ連続読み出しコマンド）
            #[.D]⇒±10進数32BIT表示・・・返り値は10桁の0埋め数値
            client.send(comand.encode("ascii"))    # 上位リンク通信のデータコードがASCIIなのでエンコード
            #print("send : " + comand)
 
            response = client.recv(64)          #受信用バイト配列を定義しておく
            response = response.decode("UTF-8") # PLCからの返答がbyteデータなのでUTF-8にデコード
  
            #print("Received :" ,int(response))
            bin_num = bin(int(response))
            NowAL.append(("0000000000000000" + str(bin_num[2:]))[-16:])
            #print("Received :" ,NowAL[c],c)
        
            #logging.debug('end')

            #異常無し→有り  前回と同bitデバイスならスルー
            if "1" in NowAL[c] and NowAL[c] != MemoryAL[c]:           
                for p in range(16):
                    if NowAL[c][15 - p:15 - p + 1] == "1" and NowAL[c][15 - p:15 - p + 1] != MemoryAL[c][15 - p:15 - p + 1]:    
                        #PLCsend[0]設備のみ経過時間、残り時間格納                 
                        for et in range(st):  
                            for fn in range(fuc_count):
                                if ALdev2d[et][fn] != "e" and fn == tempFp[0]:
                                    dt_end = datetime.datetime.now()
                                    elapsedtime =  (dt_end - starttime2d[et][fn]).total_seconds() #秒数変換
                                    elapsedtime2d[et][fn] = math.floor(elapsedtime) #小数点切り捨て
                                    remaintime2d[et][fn] = max(0, ALtime2d[et][fn] - elapsedtime2d[et][fn]) #マイナスは0                                                
                    
                        for row in range(AL_rcount):
                            for col in range(AL_ccount//6):
                                fdev_col = col * 6 + 1 #検索デバイスNo行
                                fbit_col = col * 6 + 2 #検索bitNo行
                                find_ALNo = AL_2d_all[row][fdev_col]
                                find_ALbit = AL_2d_all[row][fbit_col]
                                if find_ALNo == str(type_dev) + str(dev_No) and find_ALbit == p:                             
                                    ALdev = AL_2d_all[row][fdev_col]
                                    ALbit = int(AL_2d_all[row][fdev_col+1])
                                    ALlev = AL_2d_all[row][fdev_col+2]
                                    ALtime = int(AL_2d_all[row][fdev_col+3])
                                    ALcont = AL_2d_all[row][fdev_col+4]                               
                               
                                    fp = P_list.index(fdev_col - 1) + 1 #優先順位(1～
                                
                                    for r in range(st):                                  
                                        if ALdev2d[r][fp-1] == "e":
                                            ALdev2d[r][fp-1] = ALdev
                                            ALbit2d[r][fp-1] = ALbit
                                            if ALlev != "S" and ALlev != "A" and ALlev != "B" and ALlev != "C":
                                                ALlev2d[r][fp-1] = "A"
                                            else:
                                                ALlev2d[r][fp-1] = ALlev

                                            if ALtime != "":
                                                ALtime2d[r][fp-1] = ALtime 
                                            else:
                                                ALtime2d[r][fp-1] = 300  

                                            ALcont2d[r][fp-1] = ALcont                                                                             
                                            break                                         
                                    else:
                                        continue
                                    break
                            else:
                                continue
                            break
                    else:
                        continue
                    break
                #else:
                #    continue
                #break
        
            #異常有り⇒無し
            if NowAL[c] != MemoryAL[c]:
                 for p in range(16):
                    if NowAL[c][15 - p:15 - p + 1] == "0" and NowAL[c][15 - p:15 - p + 1] != MemoryAL[c][15 - p:15 - p + 1]: #0のままならスルー                   
                        for col in range(AL_ccount//6):
                            fdev_col = col * 6 + 1 #検索デバイスNo行                     
                            fp = P_list.index(fdev_col - 1) + 1 #優先順位(1～                                                    
                            for r in range(st):                                  
                                if ALdev2d[r][fp-1] == str(type_dev) + str(dev_No) and ALbit2d[r][fp-1] == p:
                                    ALdev2d[r][fp-1] = "e"
                                    ALbit2d[r][fp-1] = 0
                                    ALlev2d[r][fp-1] = "e"
                                    ALtime2d[r][fp-1] = 0                         
                                    ALcont2d[r][fp-1] = "e"  
                                    starttime2d[r][fp-1] = "e"
                                    elapsedtime2d[r][fp-1] = "e" 
                                    remaintime2d[r][fp-1] = "e"   
                                    break                               
                            else:
                                continue
                            break
                    else:
                        continue
                    break                      
            c = c + 1
   
        MemoryAL.clear()
        for na in range(end_dev - start_dev + 1):
            MemoryAL.append(NowAL[na])

        #各レベル計算
        for tr in range(st):
            for pc in range(fuc_count): 
                 #Sレベル異常処理
                if ALlev2d[tr][pc] == "S":             
                    for x in range(se_count):
                        if "S" in tempLev: #Sが既に格納されている時                                             
                            if pc < tempFp[x] and "S" + str(pc) not in PLCsend: #既存Sより優先度高いS発生時                                                
                                DataInsert(x, "S", pc)                                                
                                break
                        
                            if pc > tempFp[x] and "S" + str(pc) not in PLCsend and tempLev[x] != "0": #既存Sより優先度低いS発生時                                                
                                for c in range(se_count):                             
                                    if pc < tempFp[c]:     
                                        DataInsert(c, "S", pc)                             
                                        break
                                    if tempFp[c] < pc and pc < tempFp[c+1] or tempLev[c+1] != "S":
                                        DataInsert(c+1, "S", pc)                                  
                                        break                            
                                else:
                                    continue
                                break                    
                        else:    
                            DataInsert(x, "S", pc)                
                            break
                    else:
                        continue
                    break  
            
                 #Aレベル異常処理
                if ALlev2d[tr][pc] == "A":           
                    Alarm("A","S","S","S", tr, pc)
              
                 #Bレベル異常処理
                if ALlev2d[tr][pc] == "B":           
                    Alarm("B","S","A","A", tr, pc)

                 #Cレベル異常処理
                if ALlev2d[tr][pc] == "C":           
                    Alarm("C","S","A","B", tr, pc)

                #PLC出力削除
                ALlev2dnp = np.array(ALlev2d)          
                for k in range(se_count):
                    if tempFp[k] == pc and tempLev[k] == "S" and  "S" not in ALlev2dnp[:,pc] or\
                       tempFp[k] == pc and tempLev[k] == "A" and  "A" not in ALlev2dnp[:,pc] or\
                       tempFp[k] == pc and tempLev[k] == "B" and  "B" not in ALlev2dnp[:,pc] or\
                       tempFp[k] == pc and tempLev[k] == "C" and  "C" not in ALlev2dnp[:,pc] :
                         tempFp.pop(k)
                         tempLev.pop(k)
                         PLCsend.pop(k)
                         Websend.pop(k)
                         Webfac.pop(k)
                         Webalarm.pop(k)

         #PLCsend[0]が更新された瞬間、開始時間を記録（経過時間計測開始）
        if PLCsend != BPLCsend:
            if PLCsend[0] != BPLCsend[0]:
                dt_start = datetime.datetime.now()                                                              
                for r in range(st):                                  
                    if ALdev2d[r][tempFp[0]] != "e":
                        starttime2d[r][tempFp[0]] = dt_start    

                BPLCsend.clear()
                for rrs in range(len(PLCsend)):
                    BPLCsend.insert(rrs, PLCsend[rrs])
       
            updateflag = 0
            BPLCsend.clear()
            for rrs in range(len(PLCsend)):
                BPLCsend.insert(rrs, PLCsend[rrs])
            event_triger()
            break
        
    else:
        client.close()


      




