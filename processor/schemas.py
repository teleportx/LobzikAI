from typing import Any, List

from pydantic import BaseModel, Field


class TextModel(BaseModel):
    text: str


class SummarizerAIModel(TextModel):
    title: str


class SummarizerResponseModel(BaseModel):
    raw_text: str
    ai_response: SummarizerAIModel


class TestSampleModel(BaseModel):
    question: str
    answer: str


class TestMakerResponseModel(BaseModel):
    test_samples: List[TestSampleModel] = Field(default_factory=list)


class ProcessorResponseModel(BaseModel):
    summarizer_response: SummarizerResponseModel
    test_maker_response: TestMakerResponseModel | None
    messages_history: list[dict[str, Any]] # History of messages for regenerating
    total_cost: int = Field(default=0)
