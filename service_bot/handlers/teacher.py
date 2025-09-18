import asyncio

import aiohttp
from aiogram import Router, types, F, Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import config
import db
from processor import AsyncTeacherModel

router = Router()


teacher_model = AsyncTeacherModel()


async def call_teacher_model(summarized_text: str, question: str):
    async with aiohttp.ClientSession() as session:
        answer = await teacher_model(session, summarized_text, question)
    return answer


@router.message(F.text, F.reply_to_message.reply_markup.inline_keyboard[0][0].url.startswith(config.host + '/lecture/'))
async def handle_teacher(message: types.Message, dbconn: AsyncSession, bot: Bot):
    lecture_id = message.reply_to_message.reply_markup.inline_keyboard[0][0].url.replace(config.host + '/lecture/', '')

    lecture = (await dbconn.execute(
        select(db.Lecture.summarized_text)
        .where(db.Lecture.id == lecture_id)
    )).fetchone()

    if lecture is None:
        await message.reply('Lecture not found')
        return

    answer_future = asyncio.create_task(call_teacher_model(lecture.summarized_text, message.text))
    while not answer_future.done():
        await bot.send_chat_action(message.chat.id, 'typing')
        await asyncio.sleep(4)

    await message.reply(answer_future.result().text)
