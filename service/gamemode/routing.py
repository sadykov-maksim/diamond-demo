from django.urls import path

from .consumer import RoomConsumer, WheelOfFortuneConsumer

websocket_urlpatterns = [
    path(r'ws/chat/', RoomConsumer.as_asgi()),
    path(r'wheel/', WheelOfFortuneConsumer.as_asgi()),
]