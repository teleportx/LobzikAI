from typing import List

from pydantic import BaseModel, Field


class SummarizerAIModel(BaseModel):
    text: str = Field(description="Brief of lecture")
    title: str = Field(description="Topic of lecture (max length - 30 chars)", max_length=40)


class SummarizerResponseModel(BaseModel):
    raw_text: str
    ai_response: SummarizerAIModel


class TestSampleModel(BaseModel):
    question: str
    answer: str


class TestMakerResponseModel(BaseModel):
    test_samples: List[TestSampleModel]


class ProcessorResponseModel(BaseModel):
    summarizer_response: SummarizerResponseModel
    test_maker_response: TestMakerResponseModel
