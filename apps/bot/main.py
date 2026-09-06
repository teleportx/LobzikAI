import sys

sys.path.append('..')

import asyncio

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties

from libs import db
from libs import config

from libs.utils.get_bot_api_session import get_bot_api_session
import handlers
import middlewares
from libs import setup_logger
from libs import redis_storage


setup_logger.__init__('Service bot')

dp = Dispatcher(storage=redis_storage.storage)

bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode='html'), session=get_bot_api_session(config.telegram_bot_api_server))


async def start_polling():
    db.base.start(config.db_url, config.debug, config.Constants.db_pool_max_size)

    await dp.start_polling(bot)


middlewares.setup(dp)
dp.include_router(handlers.router)

if __name__ == "__main__":
    asyncio.run(start_polling())
