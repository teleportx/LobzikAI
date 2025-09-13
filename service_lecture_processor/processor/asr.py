import os
from aiohttp import ClientSession

from .base import BaseProcessor


class AsyncAudioTranscriber(BaseProcessor):
    def __init__(self, chunk_size_mb: int = 4):
        super().__init__()
        self.model = os.environ.get("ASR_MODEL", "google/gemini-2.5-flash")
        self.chunk_size = chunk_size_mb * 1024 * 1024

        self.system_prompt = """Transcribe user's audio"""

    def _format_request_body(self, audio_base64: str):
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
        return {
            "model": self.model,
            "messages": messages
        }

    async def _transcribe_chunk(self, session: ClientSession, audio_base64: str) -> str:
        """Extract texts from audiofile"""
        payload = self._format_request_body(audio_base64=audio_base64)

        async with session.post(self.url, headers=self.headers, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            result = data["choices"][0]["message"]["content"]
            return result

    async def __call__(self, session: ClientSession, audio_base64: str) -> str:
        chunks_count = (len(audio_base64) + self.chunk_size - 1) // self.chunk_size
        results = []

        for i in range(chunks_count):
            start = i * self.chunk_size
            end = (i + 1) * self.chunk_size
            chunk = audio_base64[start:end]

            text = await self._transcribe_chunk(session=session, audio_base64=chunk)
            results.append(text)

        return " ".join(results)

