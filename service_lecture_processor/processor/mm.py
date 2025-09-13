import json

from aiohttp import ClientSession

from .base import BaseProcessor

from schemas import SummarizerResponseModel
from config import mm_model


class MultiModalProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()

        self.system_prompt = """You are an assistant who makes a brief of some lecture.
        You need to consider all facts. Your result - a list of facts.
        Input - audio file of lecture, output - list of facts.
        Input data is noisy, so pay attention only at facts 
        (not dialogues, appeals or some phrases not related to lecture)
        """

        self.model = mm_model

    def _format_request_body(self, audio_base64: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.system_prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_base64,
                            "format": "mp3"
                        }
                    }
                ]
            }
        ]
        response_format = SummarizerResponseModel.model_json_schema()
        return {
            "model": self.model,
            "messages": messages,
            "response_format": response_format,
        }

    async def __call__(self, session: ClientSession, audio_base64: str):
        json_body = self._format_request_body(audio_base64=audio_base64)

        async with session.post(self.url, headers=self.headers, json=json_body) as response:
            response.raise_for_status()
            data = await response.json()
            message = json.loads(data["choices"][0]["message"]["content"])

        return SummarizerResponseModel(**message)