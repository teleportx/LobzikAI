from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class AudioProcessCallbackData(CallbackData, prefix='ap'):
    file_ids_key: str
    is_union: bool


class AudioProcessUnionCallbackData(CallbackData, prefix='apu'):
    file_ids_key: str
    is_reversed: bool


def get(file_ids_key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Single file',
        callback_data=AudioProcessCallbackData(file_ids_key=file_ids_key, is_union=True),
    )

    builder.button(
        text='Separated files',
        callback_data=AudioProcessCallbackData(file_ids_key=file_ids_key, is_union=False),
    )

    builder.adjust(2)

    return builder.as_markup()


def get_union(file_ids_key: str):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Normal',
        callback_data=AudioProcessUnionCallbackData(file_ids_key=file_ids_key, is_reversed=False),
    )

    builder.button(
        text='Reversed',
        callback_data=AudioProcessUnionCallbackData(file_ids_key=file_ids_key, is_reversed=True),
    )

    return builder.as_markup()
