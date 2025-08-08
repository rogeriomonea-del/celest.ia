# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl ca-certificates libpq-dev   && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy backend code
COPY backend /app/backend

# ensure src is on path
ENV PYTHONPATH="/app/backend/src:${PYTHONPATH}"
ENV PORT=8080
ENV APP_MODULE="api.main:app"

EXPOSE 8080

CMD uvicorn ${APP_MODULE} --host 0.0.0.0 --port ${PORT}
