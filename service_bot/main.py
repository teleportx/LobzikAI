import sys

from aiogram.client.default import DefaultBotProperties

sys.path.append('.')
sys.path.append('service_bot')

import asyncio

from aiogram import Dispatcher, Bot

import db
import config

import handlers
import middlewares

dp = Dispatcher()
bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode='html'))


async def start_polling():
    db.base.start()

    await dp.start_polling(bot)


middlewares.setup(dp)
dp.include_router(handlers.router)

if __name__ == "__main__":
    asyncio.run(start_polling())
