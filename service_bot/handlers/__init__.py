from aiogram import Router

from . import start
from . import audio

router = Router()

router.include_router(start.router)
router.include_router(audio.router)
