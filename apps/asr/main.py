import sys

sys.path.append('..')

import asyncio
import aiohttp
import hashlib
import json
from datetime import datetime
from loguru import logger

from pydantic import BaseModel, ValidationError
from aiormq.abc import DeliveredMessage

from libs import setup_logger
from libs import config
from libs.brocker import BrokerConnectionManager
from asr import ASRModel


setup_logger.__init__('Service ASR')

s3_session: aiohttp.ClientSession
model = ASRModel()


class ASRSchema(BaseModel):
    owner_id: int
    created_at: datetime
    audio_link: str


async def settle(message: DeliveredMessage, *, ack: bool, requeue: bool = False) -> None:
    try:
        if ack:
            await message.channel.basic_ack(message.delivery_tag)
        else:
            await message.channel.basic_nack(message.delivery_tag, requeue=requeue)
    except Exception:
        logger.warning('Failed to ack/nack message, it will be redelivered', exc_info=True)


async def on_message(message: DeliveredMessage):
    try:
        body = ASRSchema.model_validate_json(message.body)

    except ValidationError as e:
        logger.warning(f'Invalid message received: {message.body.decode()}\n{e}')
        await settle(message, ack=False)
        return

    try:
        async with s3_session.get(body.audio_link) as res:
            res.raise_for_status()
            audio_data = await res.read()

        audio_hash = hashlib.sha256(audio_data).hexdigest()[:8]
        logger.info(f'Start processing {audio_hash}')
        result = await model(audio_data)

        next_body = json.dumps({
            'owner_id': body.owner_id,
            'created_at': str(datetime.now().astimezone()),
            'asr_result': result,
        }, separators=(',', ':')).encode()

        await message.channel.basic_publish(
            next_body,
            routing_key='lecture_process'
        )

    except Exception:
        logger.exception('Failed to process message')
        await settle(message, ack=False, requeue=not message.delivery.redelivered)
        return

    await settle(message, ack=True)
    logger.info(f'Finish processing {audio_hash}')


async def consume_loop(connection_manager: BrokerConnectionManager):
    while True:
        try:
            async with connection_manager.acquire_channel() as channel:
                try:
                    await channel.basic_qos(prefetch_count=1)

                    queue = await channel.queue_declare(
                        'asr',
                        durable=True,
                    )

                    await channel.basic_consume(queue.queue, on_message)
                    logger.info('Consumer started')

                    while connection_manager.is_channel_alive(channel):
                        await asyncio.sleep(1)

                    logger.warning('Channel or connection lost, restarting consumer')
                finally:
                    try:
                        if not channel.is_closed:
                            await asyncio.wait_for(channel.close(), 5)
                    except Exception:
                        pass

        except Exception:
            logger.exception('Consumer crashed, restarting...')

        await asyncio.sleep(3)


async def main():
    global s3_session
    s3_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=600))

    connection_manager = BrokerConnectionManager(config.amqp_url, pool_size=4)
    await connection_manager.start()

    try:
        await consume_loop(connection_manager)
    finally:
        await connection_manager.stop()
        await s3_session.close()


if __name__ == '__main__':
    asyncio.run(main())