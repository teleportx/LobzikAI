from aiogram import Router

from . import start
from . import audio
from . import inline
from . import teacher

router = Router()

router.include_router(start.router)
router.include_router(audio.router)
router.include_router(inline.router)
router.include_router(teacher.router)
