from aiogram import Router, F, types

import brocker

router = Router()


@router.message(F.audio)
async def handle_audio(message: types.Message):
    await brocker.send_audio_to_process(message.from_user.id, message.audio.file_id)
    await message.answer('Audio has been sent for processing. We will notify you when processing is completed.')
