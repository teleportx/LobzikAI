from aiohttp import ClientSession

from multi_thread_asr import MultiThreadSpeechToText

from processor.asr import AsyncAudioTranscriber
import config


class ASRModel:
    def __init__(self):
        if config.use_local_asr:
            self.local_model = MultiThreadSpeechToText(
                workers=config.Constants.num_asr_workers,
                chunk_overlapping=config.Constants.chunk_overlapping,
            )
        else:
            self.remote_model = AsyncAudioTranscriber(
                chunk_size_mb=config.Constants.remote_asr_chunk_size_mb,
            )

    async def __call__(self, audio_base64: str) -> str:
        if not config.use_local_asr:
            async with ClientSession() as session:
                result = await self.remote_model(audio_base64=audio_base64, session=session)
        else:
            result = await self.local_model(audio_base64=audio_base64)

        return result
