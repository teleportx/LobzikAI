from aiogram import Router, F, types

import brocker

router = Router()


@router.message(F.audio)
@router.message(F.voice)
async def handle_audio(message: types.Message):
    file_id = None
    if message.voice.file_id is not None:
        file_id = message.voice.file_id

    elif message.audio.file_id is not None:
        file_id = message.audio.file_id

    await brocker.send_audio_to_process(message.from_user.id, file_id)
    await message.answer('Audio has been sent for processing. We will notify you when processing is completed.')
