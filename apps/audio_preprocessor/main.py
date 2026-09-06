import sys

sys.path.append('..')

import hashlib
import json
from datetime import datetime
import asyncio

from pydantic import BaseModel, ValidationError
from aiormq.abc import DeliveredMessage
from loguru import logger

import libs.setup_logger
from libs import config
from libs.brocker import BrokerConnectionManager
from process import process_files

libs.setup_logger.__init__('Audio Preprocessor service')


class AudioPreprocessModel(BaseModel):
    owner_id: int
    file_ids: list[str]
    created_at: datetime


def calc_list_str_hash(data: list[str]) -> str:
    hash_builder = hashlib.sha256()
    for el in data:
        hash_builder.update(el.encode())
    return hash_builder.hexdigest()


async def on_message(message: DeliveredMessage):
    try:
        body = AudioPreprocessModel.model_validate_json(message.body)

    except ValidationError as e:
        logger.warning(f'Invalid message received: {message.body.decode()}\n{e}')
        await message.channel.basic_reject(message.delivery_tag, requeue=False)
        return

    files_hash = calc_list_str_hash(body.file_ids)
    logger.info(f'Start processing {files_hash}')

    file_url = await process_files(body.file_ids)
    next_body = json.dumps({
        'owner_id': body.owner_id,
        'created_at': str(datetime.now().astimezone()),
        'audio_link': file_url,

    }, separators=(',', ':')).encode()

    await message.channel.basic_publish(
        next_body,
        routing_key='asr'
    )

    await message.channel.basic_ack(message.delivery_tag)
    logger.info(f'Finish processing {files_hash}')


async def consume_loop(connection_manager: BrokerConnectionManager):
    while True:
        try:
            async with connection_manager.acquire_channel() as channel:
                await channel.basic_qos(prefetch_count=4)

                queue = await channel.queue_declare(
                    'audio_preprocessor',
                    durable=True,
                )

                await channel.basic_consume(queue.queue, on_message)
                logger.info('Consumer started')
                await asyncio.Future()

        except Exception as e:
            logger.exception('Consumer crashed, restarting...')
            await asyncio.sleep(3)


async def main():
    connection_manager = BrokerConnectionManager(config.amqp_url, pool_size=4)
    await consume_loop(connection_manager)

if __name__ == '__main__':
    asyncio.run(main())
