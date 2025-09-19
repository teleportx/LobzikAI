import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from starlette.requests import Request
from starlette.templating import Jinja2Templates

import db

router = APIRouter(prefix='/lecture')
templates = Jinja2Templates('templates')


class LectureEditModel(BaseModel):
    summarized_text: str = Field(max_length=10 ** 6)


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


@router.patch('/{lecture_id}/edit', status_code=204)
async def handle_lecture_data(request: Request, lecture_id: uuid.UUID, body: LectureEditModel):
    # TODO: auth!!
    lecture = (await request.state.db.execute(
        update(db.Lecture)
        .where(db.Lecture.id == lecture_id)
        .values(summarized_text=body.summarized_text)
        .returning(db.Lecture.id)
    )).fetchone()

    if lecture is None:
        raise HTTPException(404, 'Lecture not found')
