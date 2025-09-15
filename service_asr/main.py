import sys

from loguru import logger

sys.path.append('.')
sys.path.append('service_asr')

import asyncio
import json
import base64
import io

from aiogram import Bot
from aiormq.abc import DeliveredMessage

import brocker
import setup_logger
import config

from utils.get_bot_api_session import get_bot_api_session

from multi_thread_asr import MultiThreadSpeechToText


setup_logger.__init__('Service ASR')

bot = Bot(config.bot_token, session=get_bot_api_session())
model = MultiThreadSpeechToText(
    workers=config.Constants.num_asr_workers,
    chunk_overlapping=config.Constants.chunk_overlapping
)


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())
    logger.info(f'Start ASR for {body['file_id']}')

    callback_topic = body['callback_topic']
    body.pop('callback_topic')

    file = io.BytesIO()
    await bot.download(body['file_id'], file)
    encoded_file = base64.b64encode(file.read()).decode()

    result = model(audio_base64=encoded_file)
    print(result)

    body['asr_result'] = result
    callback_body = json.dumps(body, separators=(',', ':')).encode()
    await message.channel.basic_publish(callback_body, routing_key=callback_topic)

    await message.channel.basic_ack(message.delivery_tag)  # set message is proceed


async def main():
    channel = await (await brocker.get_connection()).channel()
    await channel.basic_qos(prefetch_count=1)

    declare = await channel.queue_declare('asr', durable=True)
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
