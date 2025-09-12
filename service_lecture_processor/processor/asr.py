import aiohttp
import os

from .base import BaseProcessor


class AsyncAudioTranscriber(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.model = os.environ.get("ASR_MODEL", "whisper-large-v3")
        self.url = "https://openrouter.ai/api/v1/audio/transcriptions"
        self.session = aiohttp.ClientSession()

    def __del__(self):
        self.session.close()

    async def __call__(self, audio_base64: str, language: str = "ru") -> str:
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
