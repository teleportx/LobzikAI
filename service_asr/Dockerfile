FROM python:3.13.3-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential ffmpeg

COPY ./requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./service_asr/requirements.txt service_requirements.txt
RUN pip3 install --no-cache-dir -r service_requirements.txt

COPY . .

CMD ["python", "service_asr/main.py"]