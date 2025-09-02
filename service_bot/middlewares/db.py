from typing import Any, Dict, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update

import db


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        async with db.base.Session() as session:
            data['dbconn'] = session
            res = await handler(event, data)
            await session.commit()

        return res
