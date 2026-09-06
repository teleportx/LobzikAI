from aiogram import Dispatcher

from .auth_user import AuthUserMiddleware
from .db import DatabaseMiddleware
from .media_group import MediaGroupMiddleware


def setup(dp: Dispatcher):
    dp.update.outer_middleware.register(DatabaseMiddleware())
    dp.update.outer_middleware.register(AuthUserMiddleware())
