from aiogram import Router, types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import db
import keyboards.lecture

router = Router()


@router.inline_query()
async def handle_inline(query: types.InlineQuery, dbconn: AsyncSession):
    lectures = (await dbconn.execute(
        select(db.Lecture.id, db.Lecture.title, db.Lecture.created_at)
        .where(db.Lecture.owner_id == query.from_user.id)
        .order_by(db.Lecture.created_at.desc())
    )).fetchall()

    results = []
    for lec in lectures:
        formatted_datetime = lec.created_at.strftime('%d %b %Y %H:%M')
        formatted_date = lec.created_at.strftime('%d.%m %H:%M')

        results.append(types.InlineQueryResultArticle(
            id=str(lec.id),
            title=f'[{formatted_date}] {lec.title}',
            input_message_content=types.InputTextMessageContent(
                message_text=f'Lecture note <b>{lec.title}</b>\n'
                             f'<i>~ {formatted_datetime}</i>'
            ),
            reply_markup=keyboards.lecture.get(lec.id)
        ))

    await query.answer(results, cache_time=0, is_personal=True)

