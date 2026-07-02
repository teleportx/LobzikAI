from pydantic import BaseModel, Field
from typing import Any

from processor.schemas import TestMakerResponseModel


class AgentState(BaseModel):
    messages_history: list[dict[str, Any]] = Field(default_factory=list)
    extracted_text: str
    make_test: bool
    regenerate_tests: bool
    custom_instructions: str
    regeneration_instructions: str

    ai_response: str = ""
    generated_tests: TestMakerResponseModel = Field(default_factory=TestMakerResponseModel)
    title: str = ""
    total_cost: int = 0
