from aiogram import Router, F, types

from libs import brocker, keyboards

router = Router()


def extract_file_id(message: types.Message) -> str | None:
    file_id = None
    if message.voice is not None:
        file_id = message.voice.file_id

    elif message.audio is not None:
        file_id = message.audio.file_id

    elif message.video is not None:
        file_id = message.video.file_id

    return file_id


@router.message(F.audio)
@router.message(F.voice)
async def handle_audio(message: types.Message, media_group_messages: list[types.Message] | None = None):
    if media_group_messages is None:
        await brocker.send_audio_to_process(message.from_user.id, extract_file_id(message))
        await message.answer('<tg-emoji emoji-id="5440621591387980068">🔜</tg-emoji> Attachment has been sent for processing. We will notify you when processing is completed')
        return

    file_ids = [extract_file_id(el) for el in media_group_messages]
    none_warning = file_ids.count(None) != 0
    file_ids = [el for el in file_ids if el is not None]

    text = (
        '<b>Select a process mode</b>\n'
        '- Single file: All attachments are glued together into one\n'
        '- Separated files: All attachments are process separately\n'
    )

    if none_warning:
        text += '\n<tg-emoji emoji-id="5447644880824181073">⚠</tg-emoji> At least one attachment cannot be processed'

    await message.answer(text, reply_markup=keyboards.audio.get(file_ids))


@router.callback_query(keyboards.audio.AudioProcessCallbackData.filter(~F.is_union))
async def handle_audio_process_separated(callback: types.CallbackQuery):
    cbdata = keyboards.audio.AudioProcessCallbackData.unpack(callback.data)

    for file_id in cbdata.file_ids:
        await brocker.send_audio_to_process(callback.from_user.id, file_id)

    await callback.message.edit_text('<tg-emoji emoji-id="5440621591387980068">🔜</tg-emoji> Attachments has been sent for processing. We will notify you when processing is completed')

