FROM python:3.13.3-slim

WORKDIR /app

COPY apps/bot/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY libs/setup_logger libs/setup_logger
COPY libs/config libs/config
COPY libs/brocker libs/brocker
COPY libs/utils libs/utils
COPY libs/db libs/db
COPY libs/keyboards libs/keyboards
COPY libs/redis_storage libs/redis_storage

COPY libs/alembic libs/alembic
COPY alembic.ini alembic.ini

COPY apps/bot bot

WORKDIR /app/bot
CMD ["python", "main.py"]