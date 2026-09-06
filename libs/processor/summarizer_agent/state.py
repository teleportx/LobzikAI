from operator import add
from pydantic import BaseModel, Field
from typing import Annotated, Any

from ..schemas import TestMakerResponseModel


class AgentState(BaseModel):
    extracted_text: str
    make_test: bool
    custom_instructions: str = Field(default_factory=str)

    to_regenerate: bool = Field(default=False)
    previous_response: str = Field(default_factory=str)
    regenerate_tests: bool = Field(default=True)
    regeneration_instructions: str = Field(default_factory=str)
    messages_history: list[dict[str, Any]] = Field(default_factory=list)

    ai_response: str = Field(default_factory=str)
    generated_tests: TestMakerResponseModel = Field(default_factory=TestMakerResponseModel)
    title: str = Field(default_factory=str)
    total_cost: Annotated[float, add] = Field(default=0)
