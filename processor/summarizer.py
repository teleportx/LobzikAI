from openai import AsyncOpenAI

from .base import BaseProcessor
from .schemas import SummarizerResponseModel, SummarizerAIModel

import config


class AsyncTextSummarizer(BaseProcessor):
    def __init__(self, client: AsyncOpenAI):
        super().__init__()
        self.system_prompt = """You are an assistant who makes a brief of some lecture.
        You need to extract all facts from lecture. Your result - a list of facts.
        Input data is noisy, so pay attention only at facts, but save a whole sense of lecture.
        Don't lose any details about facts.
        (not dialogues, appeals or some phrases not related to lecture)
        All output data must be in markdown format. Sort all facts by their topic. 
        Before every group of facts with the same topic, put a header.
        """
        self.title_maker_prompt = """You are an assistant who makes titles.
        You are provided summarized version of some lecture. Your task - give a short title.
        Title must be shorter than 5 words, but represent main reason of lecture."""

        self.client = client

        self.model = config.AIModels.sum_model
        self.title_maker_model = config.AIModels.base_gpt_model

    async def __call__(self, text: str) -> SummarizerResponseModel:
        summarizer_messages = [
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
                        "text": f"Summarize this lecture: {text}",
                    }
                ]
            }
        ]

        title_maker_messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.title_maker_prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Give a title to lecture bellow: {text}"
                    }
                ]
            }
        ]

        summarizer_response = await self.client.responses.parse(
            model=self.model,
            input=summarizer_messages,
        )

        title_maker_response = await self.client.responses.parse(
            model=self.title_maker_model,
            input=title_maker_messages,
            max_output_tokens=32,
        )

        ai_response = SummarizerAIModel(
            title=title_maker_response.output_text,
            text=summarizer_response.output_text,
        )

        return SummarizerResponseModel(
            ai_response=ai_response,
            raw_text=text,
        )
