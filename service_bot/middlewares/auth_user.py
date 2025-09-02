from typing import Any, Dict, Callable

from aiogram import BaseMiddleware, types
from aiogram.types import Update, LinkPreviewOptions
from sqlalchemy import select, insert, update

import db


class AuthUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable,
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if 'event_from_user' not in data:
            return None

        user: types.User = data['event_from_user']

        db_user = (await data['dbconn'].execute(
            select(db.User).where(db.User.id == user.id)
        )).fetchone()

        if db_user is None:
            db_user = (await data['dbconn'].execute(
                insert(db.User).values(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                )
                .returning(db.User)
            )).fetchone()

        elif (db_user[0].first_name != user.first_name
                or db_user[0].last_name != user.last_name
                or db_user[0].username != user.username):

            db_user = (await data['dbconn'].execute(
                update(db.User).where(db.User.id == user.id)
                .values(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                )
                .returning(db.User)
            )).fetchone()

        if not db_user[0].is_whitelisted:
            await data['bot'].send_message(
                user.id,
                'You are not whitelisted in this bot. '
                'Request access from the bot administrator or <a href="https://github.com/teleportx/LobzikAI">host your own bot</a>.',
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
            return None

        data['user'] = db_user[0]

        return await handler(event, data)
