from .base import BaseProcessor
from .summarizer import AsyncTextSummarizer
from .asr import AsyncAudioTranscriber

from schemas import SummarizerResponseModel


class LectureProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()

        self.summarizer = AsyncTextSummarizer()
        self.asr = AsyncAudioTranscriber()

    async def __call__(self, audio_base64: str, language: str = "ru") -> tuple[str, SummarizerResponseModel]:
        extracted_text = await self.asr(audio_base64=audio_base64, language=language)
        summarized_text = await self.summarizer(text=extracted_text)
        return extracted_text, summarized_text
