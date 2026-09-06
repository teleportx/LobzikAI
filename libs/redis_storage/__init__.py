from os import environ

from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio.client import Redis

redis_url = environ['REDIS_URL']

storage = RedisStorage.from_url(redis_url, key_builder=DefaultKeyBuilder(with_bot_id=True))
redis: Redis = storage.redis
