import os
import requests
import zipfile
import io
from pydub import AudioSegment


def convert_audio_to_vosk_wav(audio_bytes: bytes) -> bytes:
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    return wav_io.getvalue()


def download_and_extract_zip(url: str, save_dir: str) -> None:
    os.makedirs(save_dir, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall(save_dir)
