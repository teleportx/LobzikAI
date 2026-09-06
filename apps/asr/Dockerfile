FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV KALDI_ROOT=/opt/kaldi
ENV CUDA_ROOT=/usr/local/cuda

# ---------------------------------------------------------
# System dependencies
# ---------------------------------------------------------

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    curl \
    bzip2 \
    unzip \
    xz-utils \
    ca-certificates \
    build-essential \
    g++ \
    make \
    cmake \
    automake \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------
# Build Kaldi with CUDA
# ---------------------------------------------------------

RUN git clone \
    -b vosk \
    --single-branch \
    --depth=1 \
    https://github.com/alphacep/kaldi \
    /opt/kaldi

RUN cd /opt/kaldi/tools && \
    sed -i 's:status=0:exit 0:g' extras/check_dependencies.sh && \
    sed -i 's:--enable-ngram-fsts:--enable-ngram-fsts --disable-bin:g' Makefile && \
    make -j"$(nproc)" openfst cub && \
    extras/install_openblas_clapack.sh

RUN cd /opt/kaldi/src && \
    ./configure \
        --mathlib=OPENBLAS_CLAPACK \
        --shared

RUN cd /opt/kaldi/src && \
    sed -i 's: -O1 : -O3 :g' kaldi.mk && \
    make -j"$(nproc)" \
        online2 \
        lm \
        rnnlm \
        cudafeat \
        cudadecoder

# ---------------------------------------------------------
# Build Vosk with CUDA
# ---------------------------------------------------------

RUN git clone \
    --depth=1 \
    https://github.com/alphacep/vosk-api \
    /opt/vosk-api

RUN cd /opt/vosk-api/src && \
    HAVE_CUDA=1 \
    KALDI_ROOT=/opt/kaldi \
    make -j"$(nproc)"

# ---------------------------------------------------------
# Install Python Vosk module
# ---------------------------------------------------------

RUN cd /opt/vosk-api/python && \
    python3 setup.py install

# ---------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------

WORKDIR /app

COPY apps/asr/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY libs/setup_logger.py libs/setup_logger.py
COPY libs/config.py libs/config.py
COPY libs/brocker libs/brocker
COPY libs/processor libs/processor
COPY libs/utils libs/utils

COPY apps/asr asr

WORKDIR /app/asr
CMD ["python", "main.py"]