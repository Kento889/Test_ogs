## chat/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    #path('ws/gsh/<str:room_name>/', consumers.ChatConsumer),
    path('ws/gsh/', consumers.ChatConsumer),
    ]

## chat/routing.py
#from django.urls import re_path

#from . import consumers

#websocket_urlpatterns = [
#    re_path(r'ws/chat/(?p<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
#]
