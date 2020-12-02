# chat/consumers.py
import json
from asgiref.sync import async_to_sync
#from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import asyncio
import threading


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        #self.room_name = self.scope['url_route']['kwargs']['room_name']
        #self.room_group_name = 'chat_%s' % self.room_name
        self.room_name = 'event'
        self.room_group_name = self.room_name+"_sharif"
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        #await self.channel_layer.group_add(
        #    self.room_group_name,
        #    self.channel_name
        #)
        #await self.accept()
        import chat.ReadExcel
        from chat import Dummy1
        from chat import Dummy2
        #Dummy1.main1()

        th00 = threading.Thread(target=Dummy1.main1, name="th00", args=())
        th01 = threading.Thread(target=Dummy2.main1, name="th01", args=())
        th00.start()
        th01.start()
    

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print("DISCONNECT!!")
        #await self.channel_layer.group_discard(
        #    self.room_group_name,
        #    self.channel_name
        #)


    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        #await self.channel_layer.group_send(
        #    self.room_group_name,
        #    {
        #        'type': 'chat_message',
        #        'message': message
        #    }
        #)


    def G_message(self, event):
        message = []
        for oc in range(1, 21):
            message.append(event['message' + str(oc)])
            #message2 = event['message2']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'Gmesg_fuc1': message[0],
            'Gmesg_fuc2': message[1],
            'Gmesg_fuc3': message[2],
            #'message4': message[3],
            #'message5': message[4],
            #'message6': message[5],
            #'message7': message[6],
            #'message8': message[7],
            #'message9': message[8],
            #'message10': message[9],
            'Gmesg_alarm1': message[10],
            'Gmesg_alarm2': message[11],
            'Gmesg_alarm3': message[12],
            #'message14': message[13],
            #'message15': message[14],
            #'message16': message[15],
            #'message17': message[16],
            #'message18': message[17],
            #'message19': message[18],
            #'message20': message[19]
        }))

        #await self.send(text_data=json.dumps({
        #    'message1': message[0],

        #}))
        from chat import Dummy1  
        th00 = threading.Thread(target=Dummy1.main1, name="th00", args=())
        th00.start()
        

    def H_message(self, event):
        message = []
        for oc in range(1, 21):
            message.append(event['message' + str(oc)])
            #message2 = event['message2']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            #'message1': message[0],
            #'message2': message[1],
            #'message3': message[2],
            'Hmesg_fuc1': message[0],
            'Hmesg_fuc2': message[1],
            'Hmesg_fuc3': message[2],
            #'message7': message[6],
            #'message8': message[7],
            #'message9': message[8],
            #'message10': message[9],
            #'message11': message[10],
            #'message12': message[11],
            #'message13': message[12],
            'Hmesg_alarm1': message[10],
            'Hmesg_alarm2': message[11],
            'Hmesg_alarm3': message[12],
            #'message17': message[16],
            #'message18': message[17],
            #'message19': message[18],
            #'message20': message[19]
        }))

        from chat import Dummy2
        th01 = threading.Thread(target=Dummy2.main1, name="th01", args=())
        th01.start()





