from pydantic import BaseModel

from processor.schemas import TestMakerResponseModel


class AgentState(BaseModel):
    messages_history: list | None = None
    extracted_text: str
    make_test: bool
    regenerate_tests: bool
    custom_instructions: str
    regeneration_instructions: str

    ai_response: str = ""
    generated_tests: TestMakerResponseModel | None = None
    title: str = ""
