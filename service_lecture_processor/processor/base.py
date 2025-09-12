from abc import ABC, abstractmethod
from aiohttp import ClientSession
import os


class BaseProcessor(ABC):
    def __init__(self):
        self.api_key = os.environ["OPENROUTER_KEY"]
        self.session: ClientSession = ClientSession()

    # def __del__(self):
    #     self.session.close()

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
