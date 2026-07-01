from openai import AsyncOpenAI

from processor.base import BaseProcessor
from processor.separate_processors.summarizer import AsyncTextSummarizer
from processor.separate_processors.asr import AsyncAudioTranscriber
from processor.separate_processors.test_maker import AsyncTestMaker

from processor.schemas import ProcessorResponseModel, TestMakerResponseModel


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
            asr_result = await self.asr(audio_base64)
            extracted_text = asr_result.text

        summarize_result = await self.summarizer(text=extracted_text)

        test_maker_result = TestMakerResponseModel()
        if make_test:
            test_maker_result = await self.test_maker(text=summarize_result.ai_response.text)

        return ProcessorResponseModel(
            summarizer_response=summarize_result,
            test_maker_response=test_maker_result,
        )
