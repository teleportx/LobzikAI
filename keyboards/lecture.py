import uuid

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from utils import jwt_token


class LectureMarkEditCallbackData(CallbackData, prefix='le'):
    lecture_id: uuid.UUID
    field: str
    value: bool


def get(lecture_id: uuid.UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text='View lecture',
        url=config.host + f'/lecture/{lecture_id}',
    )

    return builder.as_markup()


def get_owned(lecture_id: uuid.UUID, user_id: int, show_questions_section: bool, show_askai_section: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    jti, api_key = jwt_token.generate_token('lecture', {'user_id': user_id}, config.Constants.lecture_token_ttl)

    builder.button(
        text='View/edit lecture',
        url=config.host + f'/lecture/{lecture_id}?apikey={api_key}',
    )

    mark = ['❌', '✅']
    builder.button(
        text=mark[show_questions_section] + ' Show test questions section',
        callback_data=LectureMarkEditCallbackData(lecture_id=lecture_id, field='show_questions_section', value=not show_questions_section),
    )

    builder.button(
        text=mark[show_askai_section] + ' Show Ask AI section',
        callback_data=LectureMarkEditCallbackData(lecture_id=lecture_id, field='show_askai_section', value=not show_askai_section),
    )

    builder.adjust(1)

    return builder.as_markup()
