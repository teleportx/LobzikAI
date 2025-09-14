from multi_thread_asr import MultiThreadSpeechToText
import base64


def encode_audio_to_base64():
    with open(audio_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')


audio_path = "Обществознание.mp3"

model = MultiThreadSpeechToText(workers=8, chunk_overlapping=2.0)
encoded_audio = encode_audio_to_base64()
result = model(audio_base64=encoded_audio)
print(result)
