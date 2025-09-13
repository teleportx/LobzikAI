import os
from abc import ABC, abstractmethod

import config


class BaseProcessor(ABC):
    def __init__(self):
        self.api_key = config.openrouter_key
        self.url = "https://openrouter.ai/api/v1/chat/completions"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
