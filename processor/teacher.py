from aiohttp import ClientSession

from processor.base import BaseProcessor

from .schemas import TextModel
import config


class AsyncTeacherModel(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.system_prompt = """You are teacher. You've been provided some facts from lecture.
        Some student asks question about the lecture. Your task - give him correct answer.
        """

        self.model = config.AIModels.base_gpt_model


    def _format_request_body(self, lecture_text: str, student_question: str) -> dict:
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
        return {
            "model": self.model,
            "messages": messages,
        }

    async def __call__(
            self,
            session: ClientSession,
            lecture_text: str,
            student_question: str,
    ) -> TextModel:
        """Answer question about lecture asynchronously"""
        json_body = self._format_request_body(lecture_text=lecture_text, student_question=student_question)

        async with session.post(self.url, headers=self.headers, json=json_body) as response:
            response.raise_for_status()
            data = await response.json()
            message = data["choices"][0]["message"]["content"]

        return TextModel(
            text=message
        )
