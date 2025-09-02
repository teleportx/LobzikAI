import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette.requests import Request
from starlette.templating import Jinja2Templates

import db

router = APIRouter(prefix='/lecture')
templates = Jinja2Templates('templates')


@router.get('/{lecture_id}')
async def handle_lecture_html(request: Request, lecture_id: uuid.UUID):
    return templates.TemplateResponse(request=request, name='lecture.html', context={
        'lecture_id': lecture_id,
    })


@router.get('/{lecture_id}/data')
async def handle_lecture_data(request: Request, lecture_id: uuid.UUID):
    lecture = (await request.state.db.execute(
        select(db.Lecture.summarized_text)
        .where(db.Lecture.id == lecture_id)
    )).fetchone()

    if lecture is None:
        raise HTTPException(404, 'Lecture not found')

    return {
        'summarized_text': lecture.summarized_text
    }
