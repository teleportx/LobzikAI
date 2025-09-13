import json

from aiohttp import ClientSession

from .base import BaseProcessor

from schemas import SummarizerResponseModel
from config import sum_model


class AsyncTextSummarizer(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.system_prompt = """You are an assistant who makes a brief of some lecture.
        You need to extract all facts from lecture. Your result - a list of facts.
        Put 1 blank line between facts.
        Input data is noisy, so pay attention only at facts 
        (not dialogues, appeals or some phrases not related to lecture)
        """

        self.model = sum_model

    @staticmethod
    def _format_response_format():
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "lecture_summary",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Brief of lecture (list of facts)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Topic of lecture (max length - 30 chars)",
                            "maxLength": 40
                        }
                    },
                    "required": ["text", "title"],
                    "additionalProperties": False
                }
            }
        }

    def _format_request_body(self, lecture_text: str) -> dict:
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.system_prompt,
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Summarize this lecture: {lecture_text}"
                    }
                ]
            }
        ]
        return {
            "model": self.model,
            "messages": messages,
            "response_format": self._format_response_format(),
        }

    async def __call__(self, session: ClientSession, text: str) -> SummarizerResponseModel:
        """Summarize the given text asynchronously"""
        json_body = self._format_request_body(lecture_text=text)

        async with session.post(self.url, headers=self.headers, json=json_body) as response:
            response.raise_for_status()
            data = await response.json()
            message = json.loads(data["choices"][0]["message"]["content"])

        return SummarizerResponseModel(**message)
