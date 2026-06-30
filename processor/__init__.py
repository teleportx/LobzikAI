from openai import AsyncOpenAI

from .base import BaseProcessor
from .summarizer import AsyncTextSummarizer
from .asr import AsyncAudioTranscriber
from .test_maker import AsyncTestMaker

from .schemas import ProcessorResponseModel, TestMakerResponseModel


class LectureProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()

        self.client = AsyncOpenAI()

        self.summarizer = AsyncTextSummarizer(client=self.client)
        self.asr = AsyncAudioTranscriber(client=self.client)
        self.test_maker = AsyncTestMaker(client=self.client)

    async def __call__(
            self,
            extracted_text: str = "",
            audio_base64: str = "",
            make_test: bool = False,
    ) -> ProcessorResponseModel:

        if not extracted_text:
            if not audio_base64:
                raise ValueError("No extracted text or audio provided")
            extracted_text = await self.asr(audio_base64)

        summarize_result = await self.summarizer(text=extracted_text)

        test_maker_result = TestMakerResponseModel()
        if make_test:
            test_maker_result = await self.test_maker(text=summarize_result.ai_response.text)

        return ProcessorResponseModel(
            summarizer_response=summarize_result,
            test_maker_response=test_maker_result,
        )

