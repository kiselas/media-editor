# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/compressor/(?P<video_id>[\w-]+)/$", consumers.NotificationsConsumer.as_asgi()),
]
