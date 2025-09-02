from fastapi import APIRouter

from . import lecture

router = APIRouter()

router.include_router(lecture.router)
