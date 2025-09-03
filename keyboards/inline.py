import uuid

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config


def get(lecture_id: uuid.UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text='View lecture',
        url=config.host + f'/lecture/{lecture_id}',
    )

    return builder.as_markup()
