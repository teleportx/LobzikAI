from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette.requests import Request

import db

router = APIRouter(prefix='/lesson')


@router.get('/{lesson_id}')
async def handle_lesson_html(lesson_id: int):
    ...


@router.get('/{lesson_id}/data')
async def handle_lesson_data(request: Request, lesson_id: int):
    lesson = (await request.state.db.execute(
        select(db.Lesson.summarized_text)
        .where(db.Lesson.id == lesson_id)
    )).fetchone()

    if lesson is None:
        raise HTTPException(404, 'Lesson not found')

    return {
        'summarized_text': lesson.summarized_text
    }
