# Use a slim Python base image
FROM python:3.11-slim AS base

# System deps for building some wheels and runtime essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy source
COPY app /app/app

# Default port; uvicorn will bind to 0.0.0.0 inside container
ENV PORT=8080

# If you rely on .env, FastAPI can read via os.environ; docker-compose provides env.
EXPOSE 8080

# Start the app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]