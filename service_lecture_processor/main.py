import sys

from loguru import logger

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
from utils.get_bot_api_session import get_bot_api_session

from processor.summarizer import AsyncTextSummarizer


setup_logger.__init__('Service Lecture Processor')

lecture_processor: AsyncTextSummarizer

bot = Bot(config.bot_token, session=get_bot_api_session())


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())

    async with ClientSession() as session:
        raw_text, result = await lecture_processor(text=body["asr_result"], session=session)

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
    lecture_processor = AsyncTextSummarizer()

    channel = await (await brocker.get_connection()).channel()
    await channel.basic_qos(prefetch_count=3)

    declare = await channel.queue_declare('lecture_process', durable=True)
    logger.info('Start listen queue')
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
