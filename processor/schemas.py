from typing import List

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
    test_samples: List[TestSampleModel] = Field(default=[])
    raw_model_response: str = Field(default="")
    is_success: bool = Field(default=True)


class ProcessorResponseModel(BaseModel):
    summarizer_response: SummarizerResponseModel
    test_maker_response: TestMakerResponseModel
