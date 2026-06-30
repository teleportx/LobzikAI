from openai import AsyncOpenAI

from processor.base import BaseProcessor

from .schemas import TextModel
import config


class AsyncTeacherModel(BaseProcessor):
    def __init__(self, client: AsyncOpenAI):
        super().__init__()
        self.system_prompt = """You are teacher. You've been provided some facts from lecture.
        Some student asks question about the lecture. Your task - give him correct answer.
        If lecture doesn't contain any information about student's question - use your own knowledge.
        """

        self.model = config.AIModels.base_gpt_model
        self.client = client

    async def __call__(
            self,
            lecture_text: str,
            student_question: str,
    ) -> TextModel:
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.system_prompt,
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Lecture: {lecture_text} \n Student's question: {student_question}"
                    }
                ]
            }
        ]
        response = await self.client.responses.parse(
            model=self.model,
            input=messages,
        )

        return TextModel(
            text=response.output_text,
        )
