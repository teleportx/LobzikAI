FROM python:3.13.3-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential ffmpeg

COPY apps/audio_preprocessor/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY libs/setup_logger.py libs/setup_logger.py
COPY libs/config.py libs/config.py
COPY libs/brocker libs/brocker
COPY libs/utils libs/utils

COPY apps/audio_preprocessor audio_preprocessor

WORKDIR /app/audio_preprocessor
CMD ["python", "main.py"]