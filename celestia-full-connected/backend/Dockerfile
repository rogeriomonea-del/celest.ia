# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Chromium + fonts + libs for headless
RUN apt-get update && apt-get install -y --no-install-recommends \ 
    wget gnupg ca-certificates unzip xvfb \ 
    fonts-liberation libnss3 libgconf-2-4 libasound2 libxss1 libxtst6 libatk-bridge2.0-0 libgtk-3-0 \ 
    chromium chromium-driver build-essential libpq-dev \ 
  && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy code
COPY backend /app/backend

ENV PYTHONPATH="/app/backend/src:${PYTHONPATH}"
ENV PORT=8080
ENV APP_MODULE="api.main:app"
ENV CHROME_BIN="/usr/bin/chromium"
ENV CHROMEDRIVER_BIN="/usr/bin/chromedriver"

EXPOSE 8080
CMD uvicorn ${APP_MODULE} --host 0.0.0.0 --port ${PORT}
