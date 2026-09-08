import sys
import time

sys.path.append('.')
sys.path.append('service_asr')

import asyncio

from asr import ASRModel


def read_audio():
    with open(audio_path, "rb") as audio_file:
        return audio_file.read()


audio_path = "История.wav"

model = ASRModel()
encoded_audio = read_audio()
print("Processing started")
start = time.time()
result = asyncio.run(model(encoded_audio))
end = time.time()
print(result)
print(f"Processed in {end - start} seconds")
