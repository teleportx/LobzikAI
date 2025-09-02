import json
from datetime import datetime

from . import base


async def send_audio_to_process(owner_id: int, file_id: str):
    channel = await base.storer.get_channel()

    body = json.dumps({
        'owner_id': owner_id,
        'file_id': file_id,
        'created_at': str(datetime.now().astimezone()),

    }, separators=(',', ':')).encode()

    await channel.basic_publish(
        body,
        routing_key='lecture_to_process'
    )
