import sys

sys.path.append('..')

import asyncio
import json
from datetime import datetime
from loguru import logger

from aiogram import Bot
from sqlalchemy import insert
from aiormq.abc import DeliveredMessage
from aiogram.client.default import DefaultBotProperties

from libs import brocker
from libs import setup_logger
from libs import db
from libs import config
from libs import keyboards
from libs.utils.get_bot_api_session import get_bot_api_session

from libs.processor.summarizer_agent import SummarizerAgent


setup_logger.__init__('Service Lecture Processor')

lecture_processor: SummarizerAgent

bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode='html'), session=get_bot_api_session(config.telegram_bot_api_server))


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())

    result = await lecture_processor(
        extracted_text=body["asr_result"],
        make_test=True,
    )

    async with db.base.Session() as session:
        show_questions_section = False
        show_askai_section = False

        lecture_id = (await session.execute(
            insert(db.Lecture).values(
                owner_id=body['owner_id'],
                title=result.summarizer_response.ai_response.title,
                raw_text=result.summarizer_response.raw_text,
                summarized_text=result.summarizer_response.ai_response.text,
                show_questions_section=show_questions_section,
                show_askai_section=show_askai_section,
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

    formatted_datetime = datetime.fromisoformat(body['created_at']).strftime('%d %b %Y %H:%M')
    await bot.send_message(
        body['owner_id'],
        f'Your lecture <b>{result.summarizer_response.ai_response.title}</b> is ready!\n'
        f'<i>~ {formatted_datetime}</i>',
        reply_markup=keyboards.lecture.get_owned(lecture_id, body['owner_id'], show_questions_section, show_askai_section,
                                                 config.host, config.Constants.lecture_token_ttl, config.jwt_secret),
    )

    await message.channel.basic_ack(message.delivery_tag)  # set message is proceed


async def main():
    global lecture_processor

    db.base.start(config.db_url, config.debug, config.Constants.db_pool_max_size)
    lecture_processor = SummarizerAgent(config.AIModels.base_gpt_model, config.AIModels.sum_model, config.AIModels.asr_model)

    channel = await (await brocker.get_connection()).channel()
    await channel.basic_qos(prefetch_count=3)

    declare = await channel.queue_declare('lecture_process', durable=True)
    logger.info('Start listen queue')
    await channel.basic_consume(
        declare.queue, on_message
    )


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
