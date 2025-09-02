from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette.requests import Request
from starlette.templating import Jinja2Templates

import db

router = APIRouter(prefix='/lesson')
templates = Jinja2Templates('templates')


@router.get('/{lesson_id}')
async def handle_lesson_html(request: Request, lesson_id: int):
    return templates.TemplateResponse(request=request, name='lesson.html', context={
        'lesson_id': lesson_id,
    })


@router.get('/{lesson_id}/data')
async def handle_lesson_data(request: Request, lesson_id: int):
    lesson = (await request.state.db.execute(
        select(db.Lecture.summarized_text)
        .where(db.Lecture.id == lesson_id)
    )).fetchone()

    if lesson is None:
        raise HTTPException(404, 'Lesson not found')

    return {
        'summarized_text': lesson.summarized_text
    }
