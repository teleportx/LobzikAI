import sys


sys.path.append('.')
sys.path.append('service_bot')

import asyncio

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties

import db
import config

from utils.get_bot_api_session import get_bot_api_session
import handlers
import middlewares
import setup_logger


setup_logger.__init__('Service bot')

dp = Dispatcher()

bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode='html'), session=get_bot_api_session())


async def start_polling():
    db.base.start()

    await dp.start_polling(bot)


middlewares.setup(dp)
dp.include_router(handlers.router)

if __name__ == "__main__":
    asyncio.run(start_polling())
