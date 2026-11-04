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

from libs.brocker import BrokerConnectionManager
from libs import setup_logger
from libs import db
from libs import config
from libs import keyboards
from libs.utils.get_bot_api_session import get_bot_api_session

from libs.processor.summarizer_agent import SummarizerAgent


setup_logger.__init__('Service Lecture Processor')

lecture_processor: SummarizerAgent

bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode='html'), session=get_bot_api_session(config.telegram_bot_api_server))


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
        body = json.loads(message.body.decode())
        created_at = datetime.fromisoformat(body['created_at'])

        result = await lecture_processor(
            extracted_text=body['asr_result'],
            make_test=True,
        )

        show_questions_section = False
        show_askai_section = False

        async with db.base.Session() as session:
            lecture_id = (await session.execute(
                insert(db.Lecture).values(
                    owner_id=body['owner_id'],
                    title=result.summarizer_response.ai_response.title,
                    raw_text=result.summarizer_response.raw_text,
                    summarized_text=result.summarizer_response.ai_response.text,
                    show_questions_section=show_questions_section,
                    show_askai_section=show_askai_section,
                    created_at=created_at,
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

    except Exception:
        logger.exception('Failed to process message')
        await settle(message, ack=False, requeue=not message.delivery.redelivered)
        return

    try:
        formatted_datetime = created_at.strftime('%d %b %Y %H:%M')
        await bot.send_message(
            body['owner_id'],
            f'Your lecture <b>{result.summarizer_response.ai_response.title}</b> is ready!\n'
            f'<i>~ {formatted_datetime}</i>',
            reply_markup=keyboards.lecture.get_owned(lecture_id, body['owner_id'], show_questions_section, show_askai_section,
                                                     config.host, config.Constants.lecture_token_ttl, config.jwt_secret),
        )
    except Exception:
        logger.exception(f'Lecture {lecture_id} saved, but notification failed')

    await settle(message, ack=True)


async def consume_loop(connection_manager: BrokerConnectionManager):
    while True:
        try:
            async with connection_manager.acquire_channel() as channel:
                try:
                    await channel.basic_qos(prefetch_count=3)

                    queue = await channel.queue_declare(
                        'lecture_process',
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
    global lecture_processor

    db.base.start(config.db_url, config.debug, config.Constants.db_pool_max_size)
    lecture_processor = SummarizerAgent(
        config.AIModels.base_gpt_model,
        config.AIModels.sum_model,
        config.debug,
    )

    connection_manager = BrokerConnectionManager(config.amqp_url, pool_size=4)
    await connection_manager.start()

    try:
        await consume_loop(connection_manager)
    finally:
        await connection_manager.stop()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())