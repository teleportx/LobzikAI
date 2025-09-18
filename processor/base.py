from abc import ABC, abstractmethod

from config import openrouter_key


class BaseProcessor(ABC):
    def __init__(self):
        self.api_key = openrouter_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
