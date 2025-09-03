FROM python:3.13.3-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential

COPY ../../requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ../.. .

CMD ["uvicorn", "service_web.main:app", "--host", "0.0.0.0", "--port", "8000"]