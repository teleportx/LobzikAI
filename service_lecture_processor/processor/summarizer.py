import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from base import BaseProcessor
from service_lecture_processor.schemas import SummarizerResponseModel


class AsyncTextSummarizer(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.system_prompt = """You are an assistant who makes a brief of some lecture.
        You need to consider all facts. Your result - a list of facts.
        """

        self.model = os.environ.get("SUMMARIZATION_MODEL", "gpt-4o-mini")

        self.llm = ChatOpenAI(
            model=self.model,
            temperature=0,
            api_key=self.api_key,
        ).with_structured_output(SummarizerResponseModel)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "{text}")
        ])
        self.chain = self.prompt | self.llm

    async def __call__(self, text: str) -> SummarizerResponseModel:
        """Summarize the given text asynchronously"""
        response = await self.chain.ainvoke({"text": text})
        return response
