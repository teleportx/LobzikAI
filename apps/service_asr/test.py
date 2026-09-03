import sys

sys.path.append('.')
sys.path.append('service_asr')

import asyncio

from multi_thread_asr import MultiThreadSpeechToText


def read_audio():
    with open(audio_path, "rb") as audio_file:
        return audio_file.read()


audio_path = "Обществознание.wav"

model = MultiThreadSpeechToText(workers=8, chunk_overlapping=2.0, use_gpu=True)
encoded_audio = read_audio()
result = asyncio.run(model(encoded_audio))
print(result)
