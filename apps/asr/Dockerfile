FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        software-properties-common ca-certificates \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        python3.13 python3.13-venv python3.13-dev \
        build-essential ffmpeg \
    && python3.13 -m ensurepip --upgrade \
    && rm -rf /var/lib/apt/lists/*

COPY apps/asr/requirements.txt requirements.txt
RUN python3.13 -m pip install --no-cache-dir -r requirements.txt

COPY libs/setup_logger.py libs/setup_logger.py
COPY libs/config.py libs/config.py
COPY libs/brocker libs/brocker
COPY libs/processor libs/processor
COPY libs/utils libs/utils

COPY apps/asr asr

WORKDIR /app/asr
CMD ["python3.13", "main.py"]