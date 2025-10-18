import sys

sys.path.append('.')
sys.path.append('service_asr')

import asyncio
import json
import base64
import io
from loguru import logger

from aiogram import Bot
from aiormq.abc import DeliveredMessage

import brocker
import setup_logger
import config

from utils.get_bot_api_session import get_bot_api_session

from asr import ASRModel


setup_logger.__init__('Service ASR')

bot = Bot(config.bot_token, session=get_bot_api_session())
model = ASRModel()


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())
    logger.info(f'Start ASR for {body['file_id']}')

    callback_topic = body['callback_topic']
    body.pop('callback_topic')

    file = io.BytesIO()
    await bot.download(body['file_id'], file)
    encoded_file = base64.b64encode(file.read()).decode()

    result = await model(audio_base64=encoded_file)

    body['asr_result'] = result
    callback_body = json.dumps(body, separators=(',', ':')).encode()

    channel = await brocker.base.storer.get_channel()
    await channel.basic_publish(callback_body, routing_key=callback_topic)

    await message.channel.basic_ack(message.delivery_tag)  # set message is proceed


async def main():
    channel = await (await brocker.get_connection()).channel()
    await channel.basic_qos(prefetch_count=1)

    declare = await channel.queue_declare('asr', durable=True)
    logger.info('Start listen queue')
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
