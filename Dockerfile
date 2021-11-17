FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

LABEL maintainer Shun Fukusumi <shun.fukusumi@gmail.com>

ENV TZ Asia/Tokyo

COPY pyproject.toml poetry.lock ./

RUN pip install -U pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install -n --no-dev

COPY scripts/prestart.sh /app
COPY scripts/init_db /app/init_db
COPY ./src /app/app
