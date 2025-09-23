import uuid

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from utils import jwt_token


def get(lecture_id: uuid.UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text='View lecture',
        url=config.host + f'/lecture/{lecture_id}',
    )

    return builder.as_markup()


def get_owned(lecture_id: uuid.UUID, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    jti, api_key = jwt_token.generate_token('lecture', {'user_id': user_id}, config.Constants.lecture_token_ttl)

    builder.button(
        text='View/edit lecture',
        url=config.host + f'/lecture/{lecture_id}?apikey={api_key}',
    )

    return builder.as_markup()
