from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    def __init__(self):
        self.api_key = "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"
        self.url = "https://openrouter.ai/api/v1/chat/completions"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...
