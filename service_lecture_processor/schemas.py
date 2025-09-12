from pydantic import BaseModel, Field


class SummarizerResponseModel(BaseModel):
    text: str = Field(description="Brief of lecture")
    title: str = Field(description="Topic of lecture (max length - 30 chars)", max_length=40)
