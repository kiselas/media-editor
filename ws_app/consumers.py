import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer

from django_media_editor.constants import FileStatus
from ws_app.utils import send_to_socket_group

logger = logging.getLogger(__name__)


def get_channel_video_group_name(name):
    return "file_%s" % name


class NotificationsConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.file_id = self.scope["url_route"]["kwargs"]["file_id"]
        self.room_file_id = get_channel_video_group_name(self.file_id)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_file_id, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_file_id, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        logger.info('In recieve')
        # Send message to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_file_id, {"type": "send_ready_message", "message": message}
        # )

    def send_ready_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        self.send_json(
            {
                "msg_type": event['type'],
                "data": event['data'],
            },
        )
        logger.info('Haaaaaaaaaaaaaaaaaaaaaaaaaa')

    def send_error_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        self.send_json(
            {
                "msg_type": event['type'],
                "data": event['data'],
            },
        )
        logger.info('Haaaaaaaaaaaaaaaaaaaaaaaaaa')


def send_video_ready_msg(group_name, path_to_file):
    message = 'Video is ready'
    msg_type = 'send_ready_message'
    data = {
        'message': message,
        'path_to_file': path_to_file,
        'file_status': FileStatus.READY
    }
    send_to_socket_group(group_name, msg_type, data)


def send_error_msg(group_name):
    message = 'Error'
    msg_type = 'send_error_message'
    data = {
        'message': message,
        'file_status': FileStatus.ERROR
    }
    send_to_socket_group(group_name, msg_type, data)

