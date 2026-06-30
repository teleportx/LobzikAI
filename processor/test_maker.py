from openai import AsyncOpenAI

from .base import BaseProcessor

from .schemas import TestMakerResponseModel
import config


class AsyncTestMaker(BaseProcessor):
    def __init__(self, client: AsyncOpenAI):
        super().__init__()
        self.system_prompt = """You are teacher. You've been provided some facts from lecture.
        Your task - Make a short test with growing complexity of questions. 
        Your response 10 questions with respective answers.
        """

        self.model = config.AIModels.base_gpt_model
        self.client = client

    async def __call__(self, text: str) -> TestMakerResponseModel:
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
                        "text": f"Lecture: {text}"
                    }
                ]
            }
        ]
        response = await self.client.responses.parse(
            model=self.model,
            input=messages,
            text_format=TestMakerResponseModel,
        )

        return response.output_parsed
