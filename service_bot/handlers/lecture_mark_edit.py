from aiogram import Router, types
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

import db
import keyboards

router = Router()


@router.callback_query(keyboards.lecture.LectureMarkEditCallbackData.filter())
async def handle_lecture_mark_edit(callback: types.CallbackQuery, dbconn: AsyncSession):
    cbdata = keyboards.lecture.LectureMarkEditCallbackData.unpack(callback.data)

    lecture = (await dbconn.execute(
        update(db.Lecture)
        .values(**{cbdata.field: cbdata.value})
        .where(db.Lecture.id == cbdata.lecture_id)
        .returning(db.Lecture.show_questions_section, db.Lecture.show_askai_section)
    )).fetchone()

    await callback.message.edit_reply_markup(
        reply_markup=keyboards.lecture.get_owned(cbdata.lecture_id, callback.from_user.id, lecture.show_questions_section, lecture.show_askai_section)
    )
