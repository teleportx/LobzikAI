from aiogram import Router, types, F
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import config
import db
import keyboards

router = Router()


@router.message(F.text, F.reply_markup.inline_keyboard[0][0].url.startswith(config.host + '/lecture/'))
async def handle_lecture(message: types.Message, dbconn: AsyncSession):
    lecture_id = message.reply_markup.inline_keyboard[0][0].url.replace(config.host + '/lecture/', '')

    lecture = (await dbconn.execute(
        select(db.Lecture.id, db.Lecture.title, db.Lecture.owner_id, db.Lecture.created_at)
        .where(db.Lecture.id == lecture_id, db.Lecture.owner_id == message.from_user.id)
    )).fetchone()

    if lecture is None:
        await message.reply('Lecture not found or you are not have rights to edit it')
        return

    formatted_datetime = lecture.created_at.strftime('%d %b %Y %H:%M')
    await message.reply(
        f'Lecture <b>{lecture.title}</b> panel\n'
        f'<i>~ {formatted_datetime}</i>',
        reply_markup=keyboards.lecture.get_owned(lecture.id, lecture.owner_id),
    )
