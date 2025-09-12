import aiohttp
import os

from .base import BaseProcessor


class AsyncAudioTranscriber(BaseProcessor):
    def __init__(self, chunk_size_mb: int = 10):
        super().__init__()
        self.model = os.environ.get("ASR_MODEL", "whisper-large-v3")
        self.url = "https://openrouter.ai/api/v1/audio/transcriptions"
        self.session = aiohttp.ClientSession()
        self.chunk_size = chunk_size_mb * 1024 * 1024

    def __del__(self):
        self.session.close()

    async def _transcribe_chunk(self, audio_base64: str, language: str = "ru") -> str:
        """Extract texts from audiofile"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "audio": audio_base64,
            "language": language,
        }

        async with self.session.post(self.url, headers=headers, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("text", "")

    async def __call__(self, audio_base64: str, language: str = "ru") -> str:
        chunks_count = (len(audio_base64) + self.chunk_size - 1) // self.chunk_size
        results = []

        for i in range(chunks_count):
            start = i * self.chunk_size
            end = (i + 1) * self.chunk_size
            chunk = audio_base64[start:end]

            text = await self._transcribe_chunk(chunk, language)
            results.append(text)

        return " ".join(results)

