
import xlrd

wb = xlrd.open_workbook('C:\FA\Hアラームリスト.xlsx')
# ブック内のシート数を取得
num_of_worksheets = wb.nsheets
sheet_names = wb.sheet_names()

b_sheet = wb.sheet_by_name('基本設定')
p_sheet = wb.sheet_by_name('設備情報')
fuc_count = p_sheet.nrows - 2
AL_sheet = wb.sheet_by_name('アラームリスト')
AL_rcount = AL_sheet.nrows
AL_ccount = AL_sheet.ncols

def get_list_2d(sheet, start_row, end_row, start_col, end_col):
    return [sheet.row_values(row, start_col, end_col + 1) for row in range(start_row, end_row + 1)]

def get_list_2d_all(sheet):
    return [sheet.row_values(row) for row in range(sheet.nrows)]

#p_2d = get_list_2d(p_sheet, 2, 13, 1, 2)
b_2d_all = get_list_2d_all(b_sheet)
p_2d_all = get_list_2d_all(p_sheet)
AL_2d_all = get_list_2d_all(AL_sheet)

wb.release_resources()
del wb

#設備優先順位順に、列番号を格納
#設備優先順位順に、位置座標を格納
#設備優先順位順に、設備名を格納
P_list = []
PP_list = []
F_list = []
for pr in range(fuc_count):
    p_cell = p_2d_all[2 + pr][2]
    pp_cell = p_2d_all[2 + pr][3]
    for fc in range(fuc_count):
        AL_fac = AL_2d_all[0][0 + 6 * fc]
        if p_cell == AL_fac:          
            P_list.append(6 * fc)
            PP_list.append(int(p_2d_all[2 + pr][3]))
            F_list.append(p_cell)


type_dev = b_2d_all[6][2] #DM
start_dev = int(b_2d_all[7][2]) #開始番号
end_dev = int(b_2d_all[8][2]) #終了番号
line_len = b_2d_all[11][2] #生産ライン全長
walk_speed = b_2d_all[12][2] #歩行速度

S_comment = b_2d_all[15][2] #Sレベルコメント
A_comment = b_2d_all[16][2] #Aレベルコメント
B_comment = b_2d_all[17][2] #Bレベルコメント
C_comment = b_2d_all[18][2] #Cレベルコメント
