from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command('start'))
async def handle_start(message: types.Message):
    await message.answer('Hello to Lobzik AI bot! Send me a lecture audio recording and I will summarize it for you.')
