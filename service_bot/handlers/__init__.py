from aiogram import Router

from . import start
from . import audio
from . import inline

router = Router()

router.include_router(start.router)
router.include_router(audio.router)
router.include_router(inline.router)
