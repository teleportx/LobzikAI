import sys

sys.path.append('.')
sys.path.append('service_lecture_processor')

import asyncio
import json
import base64
from datetime import datetime
import io

from aiohttp import ClientSession
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from sqlalchemy import insert
from aiormq.abc import DeliveredMessage
from loguru import logger

import brocker
import setup_logger
import db
import config

from processor import LectureProcessor


setup_logger.__init__('Service Lecture Processor')

lecture_processor: LectureProcessor

session = None
if config.telegram_bot_api_server is not None:
    session = AiohttpSession(
        api=TelegramAPIServer.from_base(config.telegram_bot_api_server)
    )

bot = Bot(config.bot_token, session=session)


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())

    file = io.BytesIO()
    await bot.download(body['file_id'], file)
    encoded_file = base64.b64encode(file.read()).decode()
    logger.debug(f'File {body['file_id']} downloaded')

    async with ClientSession() as session:
        raw_text, result = await lecture_processor(audio_base64=encoded_file, session=session)

    async with db.base.Session() as session:
        await session.execute(
            insert(db.Lecture).values(
                owner_id=body['owner_id'],
                title=result.title,
                raw_text=raw_text,
                summarized_text=result.text,
                created_at=datetime.fromisoformat(body['created_at']),
            )
        )
        await session.commit()

    await message.channel.basic_ack(message.delivery_tag)  # set message is proceed


async def main():
    global lecture_processor

    db.base.start()
    lecture_processor = LectureProcessor()

    channel = await (await brocker.get_connection()).channel()
    await channel.basic_qos(prefetch_count=3)

    declare = await channel.queue_declare('lecture_to_process', durable=True)
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
