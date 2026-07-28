from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class AudioProcessCallbackData(CallbackData, prefix='ap'):
    file_ids: list[str]
    is_union: bool


class AudioProcessUnionCallbackData(CallbackData, prefix='apu'):
    file_ids: list[str]


def get(file_ids: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Process as a single file',
        callback_data=AudioProcessCallbackData(file_ids=file_ids, is_union=True),
    )

    builder.button(
        text='Process as a separated files',
        callback_data=AudioProcessCallbackData(file_ids=file_ids, is_union=False),
    )

    builder.adjust(1)

    return builder.as_markup()


def get_union(file_ids: list[str]):
    builder = InlineKeyboardBuilder()

    builder.button(
        text='Normal order',
        callback_data=AudioProcessUnionCallbackData(file_ids=file_ids),
    )

    file_ids.reverse()
    builder.button(
        text='Reversed order',
        callback_data=AudioProcessUnionCallbackData(file_ids=file_ids),
    )
    file_ids.reverse()

    return file_ids
