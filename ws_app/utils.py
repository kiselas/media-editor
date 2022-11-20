from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

CHANNEL_LAYER = get_channel_layer()


def send_to_socket_group(group_name: str, msg_type: str, data: dict,) -> None:
    async_to_sync(CHANNEL_LAYER.group_send)(
        group_name,
        {
            "type": msg_type,
            "data": data,
        }
    )
