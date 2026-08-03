import json
from datetime import datetime

from . import base


async def send_audio_to_process(owner_id: int, *file_ids: str):
    channel = await base.storer.get_channel()

    body = json.dumps({
        'owner_id': owner_id,
        'file_ids': file_ids,
        'created_at': datetime.now().isoformat(),

    }, separators=(',', ':')).encode()

    await channel.basic_publish(
        body,
        routing_key='audio_preprocessor'
    )
