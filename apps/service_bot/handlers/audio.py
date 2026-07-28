import uuid

from aiogram import Router, F, types

import middlewares
from libs import brocker, keyboards
from libs.redis_storage import redis

audio_router = Router()
audio_router.message.middleware(middlewares.MediaGroupMiddleware())

router = Router()
router.include_router(audio_router)


def extract_file_id(message: types.Message) -> str | None:
    file_id = None
    if message.voice is not None:
        file_id = message.voice.file_id

    elif message.audio is not None:
        file_id = message.audio.file_id

    elif message.video is not None:
        file_id = message.video.file_id

    return file_id


@audio_router.message(F.audio)
@audio_router.message(F.voice)
async def handle_audio(message: types.Message, media_group_messages: list[types.Message] | None = None):
    if media_group_messages is None:
        await brocker.send_audio_to_process(message.from_user.id, extract_file_id(message))
        await message.answer('<tg-emoji emoji-id="5440621591387980068">🔜</tg-emoji> Attachment has been sent for processing. We will notify you when processing is completed')
        return

    file_ids = [extract_file_id(el) for el in media_group_messages]
    none_warning = file_ids.count(None) != 0
    file_ids = [el for el in file_ids if el is not None]

    text = (
        '<tg-emoji emoji-id="5395444784611480792">✏️</tg-emoji> <b>Select a process mode</b>\n'
        '- Single file: All attachments are glued together into one\n'
        '- Separated files: All attachments are processed separately\n'
    )

    if none_warning:
        text += '\n<tg-emoji emoji-id="5447644880824181073">⚠</tg-emoji> At least one attachment cannot be processed'

    group_id = uuid.uuid4()
    await redis.set(
        f'process_group_file_ids:{group_id}',
        ','.join(file_ids),
        ex=60 * 60 * 24 * 7,
    )

    await message.answer(text, reply_markup=keyboards.audio.get(str(group_id)))


@router.callback_query(keyboards.audio.AudioProcessCallbackData.filter(~F.is_union))
async def handle_audio_process_separated(callback: types.CallbackQuery):
    cbdata: keyboards.audio.AudioProcessCallbackData = keyboards.audio.AudioProcessCallbackData.unpack(callback.data)

    file_ids_raw = await redis.get(f'process_group_file_ids:{cbdata.file_ids_key}')
    if file_ids_raw is None:
        await callback.answer('Message too old. Send it again', show_alert=True)
        return
    file_ids = file_ids_raw.decode().split(',')

    for file_id in file_ids:
        await brocker.send_audio_to_process(callback.from_user.id, file_id)

    await callback.message.edit_text('<tg-emoji emoji-id="5440621591387980068">🔜</tg-emoji> Attachments has been sent for separated processing. Your lecture will be ready in several minutes')


@router.callback_query(keyboards.audio.AudioProcessCallbackData.filter(F.is_union))
async def handle_audio_process_union_order(callback: types.CallbackQuery):
    cbdata: keyboards.audio.AudioProcessCallbackData = keyboards.audio.AudioProcessCallbackData.unpack(callback.data)

    await callback.message.edit_text('<tg-emoji emoji-id="5395444784611480792">✏️</tg-emoji> <b>Select order for attachments processing</b>\n'
                                     '- Normal: in the order of the message\n'
                                     '- Reversed: in the reverse order of the message',
                                     reply_markup=keyboards.audio.get_union(cbdata.file_ids_key))


@router.callback_query(keyboards.audio.AudioProcessUnionCallbackData.filter())
async def handle_audio_process_union(callback: types.CallbackQuery):
    cbdata: keyboards.audio.AudioProcessUnionCallbackData = keyboards.audio.AudioProcessUnionCallbackData.unpack(callback.data)

    file_ids_raw = await redis.get(f'process_group_file_ids:{cbdata.file_ids_key}')
    if file_ids_raw is None:
        await callback.answer('Message too old. Send it again', show_alert=True)
        return
    file_ids = file_ids_raw.decode().split(',')

    await brocker.send_audio_to_process(callback.from_user.id, *file_ids)
    await callback.message.edit_text('<tg-emoji emoji-id="5440621591387980068">🔜</tg-emoji> Attachments have been sent for joint processing. Your lecture will be ready in several minutes')
