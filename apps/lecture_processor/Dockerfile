FROM python:3.13.3-slim

WORKDIR /app

COPY apps/lecture_processor/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY libs/setup_logger libs/setup_logger
COPY libs/config libs/config
COPY libs/brocker libs/brocker
COPY libs/utils libs/utils
COPY libs/db libs/db
COPY libs/keyboards libs/keyboards
COPY libs/processor libs/processor

COPY libs/alembic libs/alembic
COPY alembic.ini alembic.ini

COPY apps/lecture_processor lecture_processor

WORKDIR /app/lecture_processor
CMD ["python", "main.py"]