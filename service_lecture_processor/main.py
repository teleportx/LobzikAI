import sys

sys.path.append('.')
sys.path.append('service_lecture_processor')

import asyncio
import json
from datetime import datetime
from loguru import logger

from aiohttp import ClientSession
from aiogram import Bot
from sqlalchemy import insert
from aiormq.abc import DeliveredMessage
from aiogram.client.default import DefaultBotProperties

import brocker
import setup_logger
import db
import config
import keyboards
from utils.get_bot_api_session import get_bot_api_session

from processor import LectureProcessor


setup_logger.__init__('Service Lecture Processor')

lecture_processor: LectureProcessor

bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode='html'), session=get_bot_api_session())


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())

    async with ClientSession() as session:
        result = await lecture_processor(
            extracted_text=body["asr_result"],
            session=session,
            make_test=False
        )

    async with db.base.Session() as session:
        lecture_id = (await session.execute(
            insert(db.Lecture).values(
                owner_id=body['owner_id'],
                title=result.summarizer_response.ai_response.title,
                raw_text=result.summarizer_response.raw_text,
                summarized_text=result.summarizer_response.ai_response.text,
                created_at=datetime.fromisoformat(body['created_at']),
            )
            .returning(db.Lecture.id)
        )).fetchone().id

        for question in result.test_maker_response.test_samples:
            await session.execute(
                insert(db.LectureTestQuestion).values(
                    lecture_id=lecture_id,
                    text=question.question,
                    answer=question.answer,
                )
            )

        await session.commit()

    print("ZOV")

    formatted_datetime = datetime.fromisoformat(body['created_at']).strftime('%d %b %Y %H:%M')
    await bot.send_message(
        body['owner_id'],
        f'Your lecture <b>{result.title}</b> is ready!\n'
        f'<i>~ {formatted_datetime}</i>',
        reply_markup=keyboards.lecture.get_owned(lecture_id, body['owner_id']),
    )

    await message.channel.basic_ack(message.delivery_tag)  # set message is proceed


async def main():
    global lecture_processor

    db.base.start()
    lecture_processor = LectureProcessor()

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
