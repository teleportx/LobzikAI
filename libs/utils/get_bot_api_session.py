from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer



def get_bot_api_session(telegram_bot_api_server: str | None):
    if telegram_bot_api_server is None:
        return None

    return AiohttpSession(
        api=TelegramAPIServer(
            base=f'{telegram_bot_api_server}/bot{{token}}/{{method}}',
            file=f'{telegram_bot_api_server}/file{{path}}',
        )
    )
