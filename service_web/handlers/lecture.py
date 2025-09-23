import uuid

import aiohttp
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from watchfiles import awatch

import db
from processor import AsyncTeacherModel
from utils.jwt_token import AuthorizeDep

router = APIRouter(prefix='/lecture')
templates = Jinja2Templates('templates')


class LectureEditModel(BaseModel):
    summarized_text: str = Field(max_length=10 ** 6)


class LectureAskModel(BaseModel):
    question: str = Field(max_length=1000)


teacher_model = AsyncTeacherModel()


async def call_teacher_model(summarized_text: str, question: str):
    async with aiohttp.ClientSession() as session:
        answer = await teacher_model(session, summarized_text, question)
    return answer


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
async def handle_lecture_data(request: Request, auth: AuthorizeDep('lecture'), lecture_id: uuid.UUID, body: LectureEditModel):
    lecture = (await request.state.db.execute(
        update(db.Lecture)
        .where(db.Lecture.id == lecture_id, db.Lecture.owner_id == auth.get('user_id'))
        .values(summarized_text=body.summarized_text)
        .returning(db.Lecture.id)
    )).fetchone()

    if lecture is None:
        raise HTTPException(404, 'Lecture not found')


@router.post('/{lecture_id}/ask')
async def handle_lecture_data(request: Request, lecture_id: uuid.UUID, body: LectureAskModel):
    lecture = (await request.state.db.execute(
        select(db.Lecture.summarized_text)
        .where(db.Lecture.id == lecture_id)
    )).fetchone()

    if lecture is None:
        raise HTTPException(404, 'Lecture not found')

    return {
        'answer': (await call_teacher_model(lecture.summarized_text, body.question)).text
    }
