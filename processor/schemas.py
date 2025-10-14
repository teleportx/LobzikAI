from typing import List

from pydantic import BaseModel, Field


class TextModel(BaseModel):
    text: str


class IsSuccessModel(BaseModel):
    is_success: bool = Field(default=True)


class SummarizerAIModel(TextModel):
    title: str


class SummarizerResponseModel(BaseModel):
    raw_text: str
    ai_response: SummarizerAIModel


class TestSampleModel(BaseModel):
    question: str
    answer: str


class TestMakerResponseModel(IsSuccessModel):
    test_samples: List[TestSampleModel] = Field(default=[])
    raw_model_response: str = Field(default="")


class ProcessorResponseModel(BaseModel):
    summarizer_response: SummarizerResponseModel
    test_maker_response: TestMakerResponseModel
