import sys

from utils.get_bot_api_session import get_bot_api_session

sys.path.append('.')
sys.path.append('service_lecture_processor')

import asyncio
import json
from datetime import datetime

from aiohttp import ClientSession
from aiogram import Bot
from sqlalchemy import insert
from aiormq.abc import DeliveredMessage

import brocker
import setup_logger
import db
import config

from processor import LectureProcessor


setup_logger.__init__('Service Lecture Processor')

lecture_processor: LectureProcessor

bot = Bot(config.bot_token, session=get_bot_api_session())


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())

    # TODO: get raw_text from body['asr_result'] and process

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

    declare = await channel.queue_declare('lecture_process', durable=True)
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
