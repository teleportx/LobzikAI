import asyncio
import io

from faster_whisper import WhisperModel, BatchedInferencePipeline
from faster_whisper.audio import decode_audio
from huggingface_hub import snapshot_download

from libs.config import ASRSettings, model_cache_dir


class ASRModel:
    def __init__(
        self,
        model_name: str = ASRSettings.model,
        device: str = ASRSettings.device,
        batch_size: int = ASRSettings.batch_size,
        compute_type: str = ASRSettings.compute_dtype,
    ):
        self.batch_size = batch_size

        local_path = snapshot_download(repo_id=model_name, local_dir=model_cache_dir)
        base_model = WhisperModel(
            local_path,
            device=device,
            compute_type=compute_type,
            local_files_only=True,
        )
        self.sampling_rate = base_model.feature_extractor.sampling_rate

        self.pipe = BatchedInferencePipeline(
            model=base_model,
        )

    def __transcribe_sync(self, audio_file: bytes) -> str:
        audio = decode_audio(io.BytesIO(audio_file), sampling_rate=self.sampling_rate)

        segments, _info = self.pipe.transcribe(
            audio,
            batch_size=self.batch_size,
            without_timestamps=True,
        )
        return " ".join(segment.text for segment in segments).strip()

    async def __call__(self, audio_file: bytes) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.__transcribe_sync, audio_file)
