from aiogram import Router

from . import start
from . import audio
from . import inline
from . import lecture
from . import lecture_mark_edit

router = Router()

router.include_router(start.router)
router.include_router(audio.router)
router.include_router(inline.router)
router.include_router(lecture.router)
router.include_router(lecture_mark_edit.router)
