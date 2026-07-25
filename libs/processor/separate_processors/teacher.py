from typing import Any

from openai import AsyncOpenAI

from ..base import BaseProcessor
from ..schemas import TeacherResponseModel


class AsyncTeacherModel(BaseProcessor):
    def __init__(self, client: AsyncOpenAI, base_gpt_model: str):
        super().__init__()
        self.system_prompt = """You are teacher. You've been provided some facts from lecture.
        Some student asks question about the lecture. Your task - give him correct answer.
        If lecture doesn't contain any information about student's question - use your own knowledge.
        """

        self.model = base_gpt_model
        self.client = client

    async def __call__(
            self,
            lecture_text: str,
            student_question: str,
            messages_history: list[dict[str, Any]] | None = None,
    ) -> TeacherResponseModel:

        new_message = {
            "role": "user",
            "content": f"Student's question: {student_question}",
        }

        if not messages_history:
            messages_history = [
                {
                    "role": "system",
                    "content": self.system_prompt + f"\nThe lecture: {lecture_text}",
                },
            ]
        messages_history.append(new_message)

        response = await self.client.responses.parse(
            model=self.model,
            input=messages_history,
        )

        return TeacherResponseModel(
            text=response.output_text,
            messages_history=messages_history,
        )
