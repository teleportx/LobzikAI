from openai import AsyncOpenAI

from processor.base import BaseProcessor
from processor.schemas import TextModel

import config


class AsyncAudioTranscriber(BaseProcessor):
    def __init__(self, client: AsyncOpenAI, chunk_size_mb: int = 4):
        super().__init__()
        self.model = config.AIModels.asr_model
        self.chunk_size = chunk_size_mb * 1024 * 1024
        self.client = client

        self.system_prompt = """Transcribe user's audio"""

    async def _transcribe_chunk(self, audio_base64: str) -> str:
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": self.system_prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_base64,
                            "format": "mp3"
                        }
                    }
                ]
            }
        ]
        response = await self.client.responses.parse(
            model=self.model,
            input=messages,
        )
        return response.output_text

    async def __call__(self, audio_base64: str) -> TextModel:
        chunks_count = (len(audio_base64) + self.chunk_size - 1) // self.chunk_size
        results = []

        for i in range(chunks_count):
            start = i * self.chunk_size
            end = (i + 1) * self.chunk_size
            chunk = audio_base64[start:end]

            text = await self._transcribe_chunk(audio_base64=chunk)
            results.append(text)

        result_string = " ".join(results)

        return TextModel(text=result_string)
