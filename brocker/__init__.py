from . import base

from .send_audio_to_process import send_audio_to_process


async def init():
    await (await base.storer.get_connection()).channel()


async def get_connection():
    return await base.storer.get_connection()
