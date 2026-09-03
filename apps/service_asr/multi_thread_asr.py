import asyncio
import io
import os
import wave
import json
import concurrent.futures

from loguru import logger
from vosk import BatchModel, BatchRecognizer, GpuInit, Model, KaldiRecognizer

from libs.utils.download_and_extract_zip import download_and_extract_zip
from libs import config


class MultiThreadSpeechToText:
    def __init__(self, workers: int = 12, chunk_overlapping: float = 2.0, use_gpu: bool = False):
        self.use_gpu = use_gpu
        self.workers = workers
        self.chunk_overlapping = chunk_overlapping
        self.model_name = config.AIModels.local_asr_vosk_model
        self.saving_path = os.path.join(config.model_cache_dir, self.model_name)

        if not os.path.exists(self.saving_path):
            logger.info("Vosk model not loaded. Start downloading...")
            download_and_extract_zip(
                url=f"https://alphacephei.com/vosk/models/{self.model_name}.zip",
                save_dir=config.model_cache_dir,
            )

        if self.use_gpu:
            logger.info("GPU initialization")
            GpuInit()
            self.model = BatchModel(self.saving_path)
        else:
            self.model = Model(model_path=self.saving_path)

    def _process_chunk_cpu(self, wav_bytes: bytes, start_frame: int, end_frame: int, framerate: int) -> str:
        with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
            wf.setpos(start_frame)
            rec = KaldiRecognizer(self.model, framerate)

            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            frame_bytes = channels * sampwidth

            result_text = ""
            frames_to_read = end_frame - start_frame

            while frames_to_read > 0:
                frames_chunk = min(4000, frames_to_read)
                data = wf.readframes(frames_chunk)
                if not data:
                    break

                frames_to_read -= len(data) // frame_bytes

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    result_text += result.get("text", "") + " "

            final_result = json.loads(rec.FinalResult())
            result_text += final_result.get("text", "")
        return result_text.strip()

    def _process_chunks_gpu(self, wav_bytes: bytes, chunks: list, framerate: int) -> list:
        channels_info = wave.open(io.BytesIO(wav_bytes), 'rb')
        channels = channels_info.getnchannels()
        sampwidth = channels_info.getsampwidth()
        frame_bytes = channels * sampwidth
        channels_info.close()

        file_handles = []
        recs = []
        remaining = []

        for start, end in chunks:
            fh = wave.open(io.BytesIO(wav_bytes), 'rb')
            fh.setpos(start)
            file_handles.append(fh)
            recs.append(BatchRecognizer(self.model, framerate))
            remaining.append(end - start)

        results = [""] * len(chunks)
        ended = set()

        try:
            while len(ended) < len(chunks):
                for i in range(len(chunks)):
                    if i in ended:
                        continue

                    frames_chunk = min(4000, remaining[i])
                    data = file_handles[i].readframes(frames_chunk)

                    if not data:
                        recs[i].FinishStream()
                        ended.add(i)
                        continue

                    remaining[i] -= len(data) // frame_bytes
                    recs[i].AcceptWaveform(data)

                    if remaining[i] <= 0:
                        recs[i].FinishStream()
                        ended.add(i)

                self.model.Wait()

                for i in range(len(chunks)):
                    res = recs[i].Result()
                    if res:
                        text = json.loads(res).get("text", "")
                        if text:
                            results[i] = (results[i] + " " + text).strip()
        finally:
            for fh in file_handles:
                fh.close()

        return results

    async def __call__(self, audio_file: bytes) -> str:
        with wave.open(io.BytesIO(audio_file), 'rb') as wf:
            framerate = wf.getframerate()
            total_frames = wf.getnframes()
            chunk_size = total_frames // self.workers
            overlap_frames = int(self.chunk_overlapping * framerate)

            chunks = []
            for i in range(self.workers):
                start = i * chunk_size
                end = (i + 1) * chunk_size if i < self.workers - 1 else total_frames

                start = max(0, start - overlap_frames if i > 0 else start)
                end = min(total_frames, end + overlap_frames if i < self.workers - 1 else end)

                chunks.append((start, end))

        loop = asyncio.get_event_loop()

        results = []
        if self.use_gpu:
            results = await loop.run_in_executor(
                None, self._process_chunks_gpu, audio_file, chunks, framerate
            )
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
                futures = [
                    loop.run_in_executor(
                        executor,
                        self._process_chunk_cpu,
                        audio_file, start, end, framerate
                    )
                    for start, end in chunks
                ]
                results = await asyncio.gather(*futures)

        return " ".join(results).strip()
