import json

from aiohttp import ClientSession

from .base import BaseProcessor

from schemas import TestMakerResponseModel
import config


class AsyncTestMaker(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.system_prompt = """You are teacher. You've been provided some facts from lecture.
        Your task - Make a short test with growing complexity of questions. 
        Your response 10 questions with respective answers.
        """

        self.model = config.AIModels.base_gpt_model

    @staticmethod
    def _format_response_format():
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "test_maker_response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "test_samples": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {
                                        "type": "string",
                                        "description": "A test question"
                                    },
                                    "answer": {
                                        "type": "string",
                                        "description": "The correct answer to the question"
                                    }
                                },
                                "required": ["question", "answer"],
                                "additionalProperties": False,
                            },
                            "description": "A list of test questions containing questions and answers"
                        }
                    },
                    "required": ["test_samples"],
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
                        "text": f"Lecture: {lecture_text}"
                    }
                ]
            }
        ]
        return {
            "model": self.model,
            "messages": messages,
            "response_format": self._format_response_format(),
        }

    async def __call__(self, session: ClientSession, text: str) -> TestMakerResponseModel:
        """Make test about lecture asynchronously"""
        json_body = self._format_request_body(lecture_text=text)

        async with session.post(self.url, headers=self.headers, json=json_body) as response:
            response.raise_for_status()
            data = await response.json()
            message = json.loads(data["choices"][0]["message"]["content"])

        return TestMakerResponseModel(
            test_samples=message
        )
