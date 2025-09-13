import sys

sys.path.append('.')
sys.path.append('service_bot')

import asyncio
from loguru import logger

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

import db
import config

import handlers
import middlewares
import setup_logger


setup_logger.__init__('Service bot')

dp = Dispatcher()

session = None
if config.telegram_bot_api_server is not None:
    logger.info(f'Use telegram API server {config.telegram_bot_api_server}')
    session = AiohttpSession(
        api=TelegramAPIServer(
            base=f'{config.telegram_bot_api_server}/bot{{token}}/{{method}}',
            file=f'{config.telegram_bot_api_server}/file/bot{{token}}{{path}}',
        )
    )

bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode='html'), session=session)


async def start_polling():
    db.base.start()

    await dp.start_polling(bot)


middlewares.setup(dp)
dp.include_router(handlers.router)

if __name__ == "__main__":
    asyncio.run(start_polling())
