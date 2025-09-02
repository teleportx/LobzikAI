import sys

sys.path.append('.')
sys.path.append('service_bot')

import asyncio

from aiogram import Dispatcher, Bot

import db
import config

import handlers

dp = Dispatcher()
bot = Bot(config.bot_token)


async def start_polling():
    db.base.start()

    await dp.start_polling(bot)


dp.include_router(handlers.router)

if __name__ == "__main__":
    asyncio.run(start_polling())
