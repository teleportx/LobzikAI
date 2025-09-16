from aiohttp import ClientSession

from .base import BaseProcessor
from .summarizer import AsyncTextSummarizer
from .asr import AsyncAudioTranscriber
from .test_maker import AsyncTestMaker

from service_lecture_processor.schemas import ProcessorResponseModel


class LectureProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()

        self.summarizer = AsyncTextSummarizer()
        self.asr = AsyncAudioTranscriber()
        self.test_maker = AsyncTestMaker()

    async def __call__(self, session: ClientSession, extracted_text: str) -> ProcessorResponseModel:
        summarize_result = await self.summarizer(text=extracted_text, session=session)
        test_maker_result = await self.test_maker(text=summarize_result.ai_response.text, session=session)

        return ProcessorResponseModel(
            summarizer_response=summarize_result,
            test_maker_response=test_maker_result,
        )

