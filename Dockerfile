# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Install system dependencies for Chromium and ChromeDriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    ca-certificates \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_BIN=/usr/bin/chromedriver

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY app ./app
COPY .env.example ./.env.example

EXPOSE 8080

# Default to binding on 0.0.0.0 inside container; external exposure is controlled by runtime
ENV BIND_HOST=0.0.0.0 \
    PORT=8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import sys,http.client; c=http.client.HTTPConnection('127.0.0.1',8080,timeout=3);\n\
    c.request('GET','/health'); r=c.getresponse(); sys.exit(0 if r.status==200 else 1)"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
