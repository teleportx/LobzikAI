import base64
import io
import os
import wave
import json
import concurrent.futures
from vosk import Model, KaldiRecognizer

from utils.download_and_extract_zip import download_and_extract_zip
from utils.convert_audio_to_vosk_wav import convert_audio_to_vosk_wav

import config


class MultiThreadSpeechToText:
    def __init__(self, workers: int = 12, chunk_overlapping: float = 2.0):
        self.model_name = config.AIModels.local_asr_vosk_model
        self.saving_path = os.path.join(config.model_cache_dir, self.model_name)

        if not os.path.exists(self.saving_path):
            download_and_extract_zip(
                url=f"https://alphacephei.com/vosk/models/{self.model_name}.zip",
                save_dir=config.model_cache_dir,
            )

        self.model = Model(model_path=self.saving_path)
        self.workers = workers
        self.chunk_overlapping = chunk_overlapping

    def _process_chunk(self, wav_bytes: bytes, start_frame: int, end_frame: int, framerate: int) -> str:
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

    def __call__(self, audio_base64: str) -> str:
        """Get text from audiofile, split into N chunks and process in parallel."""
        audio_file = base64.b64decode(audio_base64)

        wav_bytes = convert_audio_to_vosk_wav(audio_file)

        with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
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

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [
                executor.submit(self._process_chunk, wav_bytes, start, end, framerate)
                for start, end in chunks
            ]
            results = [f.result() for f in futures]

        return " ".join(results).strip()
