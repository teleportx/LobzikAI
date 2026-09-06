from openai import AsyncOpenAI

from multi_thread_asr import MultiThreadSpeechToText

from libs.processor.separate_processors import AsyncAudioTranscriber
from libs import config


class ASRModel:
    def __init__(self):
        self.client = AsyncOpenAI()

        if config.use_local_asr:
            self.model = MultiThreadSpeechToText(
                workers=config.Constants.num_asr_workers,
                chunk_overlapping=config.Constants.chunk_overlapping,
                use_gpu=config.use_gpu,
            )
        else:
            raise NotImplemented
            self.model = AsyncAudioTranscriber(
                chunk_size_mb=config.Constants.remote_asr_chunk_size_mb,
                client=self.client,
            )

    async def __call__(self, audio_file: bytes) -> str:
        result = await self.model(audio_file=audio_file)

        return result
