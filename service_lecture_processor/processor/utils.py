import base64

def encode_audio(audio_path: bytes) -> str:
    with open(audio_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
