import sys

from sqlalchemy import insert

sys.path.append('.')
sys.path.append('service_lecture_processor')

import asyncio
import json

from aiormq.abc import DeliveredMessage

import brocker
import setup_logger
import db

from processor import LectureProcessor


setup_logger.__init__('Service Lecture Processor')

lecture_processor = LectureProcessor()


async def on_message(message: DeliveredMessage):
    body = json.loads(message.body.decode())

    raw_text, result = await lecture_processor(audio_base64=body["file"])

    async with db.base.Session() as session:
        await session.execute(
            insert(db.Lecture).values(
                owner_id=body['owner_id'],
                title = result.title,
                raw_text=raw_text,
                summarized_text=result.text,
                created_at=body['created_at'],
            )
        )
        await session.commit()

    await message.channel.basic_ack(message.delivery_tag)  # set message is proceed


async def main():
    db.base.start()

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
