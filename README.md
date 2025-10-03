# SmartMedical Automation Service (Python + FastAPI)

A lightweight microservice that automates SmartMedical website interactions (timetable lookup and booking) via Selenium and exposes a secure HTTP API for n8n/WhatsApp workflows.

Important: The actual SmartMedical scraping and booking automation is intentionally left unimplemented. The service includes a clean, tested scaffold with secure endpoints that currently return 501 Not Implemented, ready for you to plug in the Selenium logic.


## Features
- FastAPI microservice with two core endpoints:
  - GET /timetable → return available time slots for a doctor
  - POST /book → perform a booking with provided details
- Security-first:
  - Local network binding by default (127.0.0.1)
  - API key authentication (X-API-Key)
  - In-memory token-bucket rate limiting (configurable)
  - PII-safe logging (does not log patient names, phone, email, etc.)
- Robust structure:
  - Clear config via environment variables/.env
  - Async timeouts around requests
  - Structured error responses
- Docker image with headless Chromium + ChromeDriver ready for Selenium


## Architecture Overview
- Python 3.11
- FastAPI for REST API
- Selenium (headless Chrome) for browser automation
- Uvicorn ASGI server
- Deployed next to n8n (e.g., via Coolify) and accessed over local/private network

Key modules:
- app/config.py – Pydantic settings from env/.env
- app/logging_config.py – PII-safe logging
- app/security.py – API key dependency and principal hashing
- app/rate_limit.py – in-memory token-bucket limiter
- app/schemas.py – Pydantic models for requests/responses
- app/errors.py – consistent error responses
- app/selenium_client.py – Selenium setup + SmartMedicalClient placeholders
- app/main.py – FastAPI app, endpoints, CORS, timeouts


## Security Model
- Bind to 127.0.0.1 by default (BIND_HOST) – prevents public exposure unless explicitly configured
- API key required in header: X-API-Key
- Rate limiting to prevent abuse (RATE_LIMIT_PER_MIN and RATE_LIMIT_BURST)
- PII-safe logging (filters sensitive keys in log extras)


## Quickstart (Local)
1) Clone and enter the project directory.

2) Create a virtual environment and install dependencies:
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt

3) Configure environment:
   - Copy .env.example to .env
   - Set API_KEY to a strong random value

4) Run the service:
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8080

5) Smoke test:
   curl http://127.0.0.1:8080/health
   curl -H "X-API-Key: <your-key>" "http://127.0.0.1:8080/timetable?doctor=Dr%20X&date=2025-12-01"

Note: Timetable and booking currently return 501 Not Implemented until Selenium logic is added.


## Docker
Build the image:
  docker build -t smartmedical-api:latest .

Run the container (local only exposure):
  docker run --rm -e API_KEY=change-me -e BIND_HOST=0.0.0.0 -p 8080:8080 smartmedical-api:latest

Consider running behind a private network or reverse proxy. Keep the service non-public.


## Environment Variables (.env)
- API_KEY: required shared secret for clients
- BIND_HOST: default 127.0.0.1 (use 0.0.0.0 inside container)
- PORT: default 8080
- RATE_LIMIT_PER_MIN: default 30
- RATE_LIMIT_BURST: default 60
- ALLOWED_ORIGINS: comma-separated origins or *
- REQUEST_TIMEOUT: timeout in seconds for each API operation (default 60)
- SELENIUM_PAGELOAD_TIMEOUT: default 30
- SELENIUM_IMPLICIT_WAIT: default 5
- BROWSER: headless-chrome (reserved; currently Chrome is used)
- CHROME_BINARY_PATH: optional path (if using custom Chrome)
- CHROMEDRIVER_PATH: optional path (if using custom chromedriver)
- LOG_LEVEL: INFO by default
- LOG_JSON: false by default (set true for JSON logs)


## API
Headers: X-API-Key: <secret>

GET /health
- 200: {"status": "ok"}

GET /timetable
- Query params:
  - doctor: optional string
  - date: optional ISO date (YYYY-MM-DD)
- Success (placeholder): 200 with TimetableResponse (currently empty slots)
- Current behavior: 501 Not Implemented
- Error responses: 401, 429, 501, 500

POST /book
- Body:
  {
    "doctor": "Dr X",
    "date": "2025-12-01",
    "time": "10:30",
    "patient": { "first_name": "A", "last_name": "B", "phone": "..." },
    "notes": "optional"
  }
- Success (placeholder): 200 with BookingResponse
- Current behavior: 501 Not Implemented
- Error responses: 401, 429, 501, 500

Error schema (typical):
  { "error": "<code or message>", "detail": <optional details> }


## Rate Limiting
- Token-bucket per principal (API key hash)
- Configurable via RATE_LIMIT_PER_MIN and RATE_LIMIT_BURST
- Returns HTTP 429 when exceeded


## Logging
- PII-safe: filters out known sensitive fields from log extras
- Toggle format with LOG_JSON


## Implementing Selenium Logic (to be done later)
- app/selenium_client.py contains:
  - browser(): context manager for a headless Chrome WebDriver
  - SmartMedicalClient.get_timetable(...): raise NotImplementedError
  - SmartMedicalClient.book(...): raise NotImplementedError
- Implementation guidance:
  - Use new clean browser per request
  - Navigate SmartMedical pages, wait for elements, extract data
  - Map results to schemas (TimetableResponse, BookingResponse)
  - Be robust to layout changes via well-named selectors and utility wait helpers
  - Ensure no PII is logged


## Deployment (example via Coolify)
- Build and deploy the Docker image alongside n8n on the same server
- Bind service to internal network only (no public exposure)
- Provide n8n with the internal base URL and API key
- Monitor logs; update selectors if the website changes


## Testing
Run unit tests locally:
  pytest -q

Tests cover:
- /health returns 200
- Auth required for protected endpoints
- Not implemented behavior for /timetable and /book (501)
- Simple rate limit scenario (429)


## Roadmap / Future Work
- Implement actual SmartMedical Selenium logic for timetable scraping and booking
- Add structured observability (metrics, traces) if needed
- Harden Docker image (non-root, read-only FS) if required