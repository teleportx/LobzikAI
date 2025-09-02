from fastapi import APIRouter

from . import lesson

router = APIRouter()

router.include_router(lesson.router)
