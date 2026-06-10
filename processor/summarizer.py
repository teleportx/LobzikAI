from aiohttp import ClientSession

from .base import BaseProcessor
from .schemas import SummarizerResponseModel, SummarizerAIModel

import config


class AsyncTextSummarizer(BaseProcessor):
    def __init__(self):
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

        self.model = config.AIModels.sum_model
        self.title_maker_model = config.AIModels.base_gpt_model

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
            "max_tokens": len(lecture_text) // 4,
            "temperature": 0,
        }

    def _format_title_maker_request_body(self, summarized_lecture_text: str) -> dict:
        messages = [
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
                        "text": f"Give a title to lecture bellow: {summarized_lecture_text}"
                    }
                ]
            }
        ]
        return {
            "model": self.title_maker_model,
            "messages": messages,
            "max_tokens": 32,
            "temperature": 0.5,
        }

    async def __call__(self, session: ClientSession, text: str) -> SummarizerResponseModel:
        """Summarize the given text asynchronously"""
        summarizer_request_body = self._format_request_body(lecture_text=text)

        async with session.post(self.url, headers=self.headers, json=summarizer_request_body) as response:
            response.raise_for_status()
            data = await response.json()
            summarized_lecture = data["choices"][0]["message"]["content"]

        title_maker_request_body = self._format_title_maker_request_body(summarized_lecture)

        async with session.post(self.url, headers=self.headers, json=title_maker_request_body) as response:
            response.raise_for_status()
            data = await response.json()
            title = data["choices"][0]["message"]["content"]

        ai_response = SummarizerAIModel(
            title=title,
            text=summarized_lecture,
        )

        return SummarizerResponseModel(
            ai_response=ai_response,
            raw_text=text,
        )
