FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1     PYTHONDONTWRITEBYTECODE=1     PIP_NO_CACHE_DIR=1     PYTHONPATH="/app/backend/src:${PYTHONPATH}"

# deps for building & chromium
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential curl ca-certificates     chromium chromium-driver     && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN="/usr/bin/chromium"     CHROMEDRIVER_BIN="/usr/bin/chromedriver"

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --upgrade pip wheel setuptools && pip install -r backend/requirements.txt

COPY backend/ /app/backend/

EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
