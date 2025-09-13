from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

import config


def get_bot_api_session():
    if config.telegram_bot_api_server is None:
        return None

    return AiohttpSession(
        api=TelegramAPIServer(
            base=f'{config.telegram_bot_api_server}/bot{{token}}/{{method}}',
            file=f'{config.telegram_bot_api_server}/file{{path}}',
        )
    )
