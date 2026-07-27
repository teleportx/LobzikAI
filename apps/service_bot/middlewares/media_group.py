import asyncio
from typing import Callable, Any

from aiogram import BaseMiddleware, types

from libs.redis_storage import redis


class MediaGroupMiddleware(BaseMiddleware):
    latency = 1

    async def __call__(
        self,
        handler: Callable,
        message: types.Message,
        data: dict[str, Any]
    ) -> Any:
        if message.media_group_id is None:
            return await handler(message, data)

        rkey = f'media_group_data_{message.media_group_id}'

        pipe = redis.pipeline(transaction=True)
        await pipe.rpush(rkey, message.model_dump_json())
        await pipe.expire(rkey, self.latency * 10)
        ress = await pipe.execute()

        list_len = ress[0]
        if list_len > 1:
            return None

        await asyncio.sleep(self.latency)
        messages_data = await redis.lrange(rkey, 0, -1)

        data['media_group_messages'] = [types.Message.model_validate_json(el) for el in messages_data]

        return await handler(message, data)
