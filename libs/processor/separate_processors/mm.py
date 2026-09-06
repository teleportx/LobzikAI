from openai import AsyncOpenAI

from ..base import BaseProcessor

from ..schemas import SummarizerResponseModel


class MultiModalProcessor(BaseProcessor):
    def __init__(self, client: AsyncOpenAI, mm_model: str):
        super().__init__()

        self.system_prompt = """You are an assistant who makes a brief of some lecture.
        You need to consider all facts. Your result - a list of facts.
        Input - audio file of lecture, output - list of facts.
        Input data is noisy, so pay attention only at facts 
        (not dialogues, appeals or some phrases not related to lecture)
        """

        self.model = mm_model
        self.client = client

    async def __call__(self, audio_base64: str):
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

        response = await self.client.responses.parse(
            model=self.model,
            input=messages,
            text_format=SummarizerResponseModel,
        )

        return response.output_parsed
