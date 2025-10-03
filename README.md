# SmartMedical Automation Service (Python + FastAPI)

A lightweight microservice that automates SmartMedical website interactions (timetable lookup and booking) via Selenium and exposes a secure HTTP API for n8n/WhatsApp workflows.

Status: Selenium automation is intentionally not implemented yet. Endpoints are secure and scaffolded and will currently return 501 Not Implemented for business operations. The service includes timeouts and rate limiting.


## Features
- FastAPI microservice with two core endpoints:
  - GET /timetable → return available time slots for a doctor (placeholder)
  - POST /book → perform a booking with provided details (placeholder)
- Security-first:
  - Local network binding by default (127.0.0.1)
  - API key authentication (X-API-Key)
  - In-memory token-bucket rate limiting (configurable)
  - PII-safe logging (does not log patient names, phone, email, etc.)
- Robust structure:
  - Clear config via environment variables/.env
  - Async timeouts around requests (returns 504 on timeout)
  - Structured error responses (stable error schema)
- Selenium ready:
  - Local ChromeDriver or Remote WebDriver via SELENIUM_REMOTE_URL
  - Headless Chrome by default
- Docker image for containerized deployment


## Architecture Overview
- Python 3.11
- FastAPI for REST API
- Selenium (headless Chrome) for browser automation
- Uvicorn ASGI server
- Typically deployed next to n8n and accessed over a private network

Key modules:
- app/core/config.py – Pydantic settings from env/.env
- app/infrastructure/logging_config.py – PII-safe logging
- app/infrastructure/security.py – API key dependency and principal hashing (X-API-Key)
- app/infrastructure/rate_limit.py – in-memory token-bucket limiter
- app/core/schemas.py – Pydantic models for requests/responses
- app/core/exceptions.py – consistent error responses
- app/infrastructure/selenium_client.py – Selenium setup + SmartMedicalClient placeholders (NotImplementedError)
- app/api/app.py – FastAPI app, routers, CORS, timeouts, security headers
- app/main.py – entrypoint wrapper (uvicorn app:app)


## Security Model
- Bind to 127.0.0.1 by default (BIND_HOST) – prevents public exposure unless explicitly configured
- API key required in header: X-API-Key
- Rate limiting to prevent abuse (RATE_LIMIT_PER_MIN and RATE_LIMIT_BURST)
- PII-safe logging (filters sensitive fields)
- Security headers: X-Content-Type-Options, X-Frame-Options, Cache-Control


## Quickstart on Windows (PowerShell)
1) Clone and enter the project directory.

2) Create a virtual environment and install dependencies:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

3) Configure environment:
   - Copy example env and set a strong API key
     Copy-Item .env.example .env
     notepad .env
   - Or set environment variables temporarily in this PowerShell session:
     $env:API_KEY = [guid]::NewGuid().ToString()
     $env:BIND_HOST = "127.0.0.1"
     $env:PORT = "8080"

4) Run the service (either CLI or Python):
   # Using uvicorn CLI
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
   # Or run the app entrypoint (reads .env)
   python -m app.main

5) Smoke tests (Windows, curl):
   curl http://127.0.0.1:8080/health
   $env:API_KEY = (Get-Content .env | Select-String '^API_KEY=' | ForEach-Object { $_.ToString().Split('=')[1] })
   curl -H "X-API-Key: $env:API_KEY" "http://127.0.0.1:8080/timetable?doctor=Dr%20X&date=2025-12-01"

Note: /timetable and /book currently return 501 Not Implemented until Selenium logic is added.


## Docker
Build the image:
  docker build -t smartmedical-api:latest .

Run the container (expose on localhost only):
  docker run --rm -e API_KEY=change-me -e BIND_HOST=0.0.0.0 -e PORT=8080 -p 8080:8080 smartmedical-api:latest

Example with Remote Selenium (Selenium Grid/Standalone Chrome):
- Start a Selenium container (example):
  docker run -d --name selenium -p 4444:4444 -p 7900:7900 selenium/standalone-chrome:latest
- Run API pointing to it:
  docker run --rm -p 8080:8080 \
    -e API_KEY=change-me \
    -e BIND_HOST=0.0.0.0 \
    -e SELENIUM_REMOTE_URL=http://host.docker.internal:4444/wd/hub \
    smartmedical-api:latest

Security tip: Keep this service non-public; use private networks or a reverse proxy with authentication.


## Environment Variables (.env)
- API_KEY: required shared secret for clients
- BIND_HOST: default 127.0.0.1 (use 0.0.0.0 inside container)
- PORT: default 8080
- RATE_LIMIT_PER_MIN: default 30
- RATE_LIMIT_BURST: default 60
- ALLOWED_ORIGINS: comma-separated origins or * (default "*")
- REQUEST_TIMEOUT: timeout in seconds for each API operation (default 60)
- SELENIUM_PAGELOAD_TIMEOUT: default 30
- SELENIUM_IMPLICIT_WAIT: default 5
- BROWSER: headless-chrome (default) or chrome (set to 'chrome' to run non-headless locally)
- CHROME_BINARY_PATH: optional path (if using custom Chrome)
- CHROMEDRIVER_PATH: optional path (if using custom chromedriver)
- SELENIUM_REMOTE_URL: optional Remote WebDriver URL (e.g., http://localhost:4444/wd/hub)
- SMARTMEDICAL_BASE_URL: default https://vm528.smartmedical.eu/
- SMARTMEDICAL_USERNAME: optional username for SmartMedical portal
- SMARTMEDICAL_PASSWORD: optional password
- SMARTMEDICAL_LOGIN_ON_TIMETABLE: false by default; if true, attempts login before timetable calls
- LOG_LEVEL: INFO by default
- LOG_JSON: false by default (set true for JSON logs)

Example .env snippet:
  API_KEY=your-very-strong-secret
  BIND_HOST=127.0.0.1
  PORT=8080
  RATE_LIMIT_PER_MIN=30
  RATE_LIMIT_BURST=60
  ALLOWED_ORIGINS=*
  REQUEST_TIMEOUT=60
  SELENIUM_PAGELOAD_TIMEOUT=30
  SELENIUM_IMPLICIT_WAIT=5
  BROWSER=headless-chrome
  # SELENIUM_REMOTE_URL=http://localhost:4444/wd/hub
  SMARTMEDICAL_BASE_URL=https://vm528.smartmedical.eu/
  # SMARTMEDICAL_USERNAME=
  # SMARTMEDICAL_PASSWORD=
  SMARTMEDICAL_LOGIN_ON_TIMETABLE=false
  LOG_LEVEL=INFO
  LOG_JSON=false


## API Reference and Useful Commands
Headers: X-API-Key: <secret>

- Health (no auth):
  curl http://127.0.0.1:8080/health
  Invoke-RestMethod -Uri http://127.0.0.1:8080/health -Method GET

- Timetable (GET) examples:
  # Missing API key → 401
  curl "http://127.0.0.1:8080/timetable?doctor=Dr%20X&date=2025-12-01"
  
  # With API key (PowerShell env var)
  $env:API_KEY = "change-me"
  curl -H "X-API-Key: $env:API_KEY" "http://127.0.0.1:8080/timetable?doctor=Dr%20X&date=2025-12-01"
  
  # Using Invoke-RestMethod
  $headers = @{ "X-API-Key" = $env:API_KEY }
  Invoke-RestMethod -Uri "http://127.0.0.1:8080/timetable?doctor=Dr%20X&date=2025-12-01" -Headers $headers -Method GET

- Booking (POST) examples:
  # PowerShell: build JSON and send
  $booking = @{ 
    doctor = "Dr X"; date = "2025-12-01"; time = "10:30"; 
    patient = @{ first_name = "Alice"; last_name = "Doe"; phone = "+370600000" }; 
    notes = "n/a" 
  } | ConvertTo-Json -Depth 5
  Invoke-RestMethod -Uri http://127.0.0.1:8080/book -Method POST -Headers $headers -Body $booking -ContentType 'application/json'
  
  # curl with JSON (Windows)
  curl -H "X-API-Key: $env:API_KEY" -H "Content-Type: application/json" -d '{"doctor":"Dr X","date":"2025-12-01","time":"10:30","patient":{"first_name":"Alice","last_name":"Doe","phone":"+370600000"}}' http://127.0.0.1:8080/book

- Rate limit quick test (expect some 429s):
  1..50 | ForEach-Object { try { Invoke-RestMethod -Uri http://127.0.0.1:8080/health -Method GET | Out-Null; Write-Host "ok" } catch { Write-Host $_.Exception.Response.StatusCode } }

- Timetable login-on-demand (if SMARTMEDICAL_LOGIN_ON_TIMETABLE=true):
  # The service will attempt a SmartMedical login before calling timetable (still placeholder).

- Timeout behavior:
  # If REQUEST_TIMEOUT is low and an operation takes longer, the API returns 504 with body {"error":"TIMEOUT"}.


## Error codes and typical responses
- 200 OK: successful health check; business endpoints return placeholder success bodies when implemented.
- 401 Unauthorized: missing/invalid X-API-Key.
- 429 Too Many Requests: rate limit exceeded.
- 500 Internal Server Error: unhandled error (returns {"error": "INTERNAL_ERROR"}).
- 501 Not Implemented: business logic not yet implemented.
- 504 Gateway Timeout: REQUEST_TIMEOUT exceeded.


## Implementing Selenium Logic (to be done later)
- app/infrastructure/selenium_client.py contains:
  - browser(): context manager for a configured Chrome WebDriver (local or remote)
  - SmartMedicalClient.get_timetable(...): raise NotImplementedError
  - SmartMedicalClient.book(...): raise NotImplementedError
- Guidance:
  - Use a fresh browser per request
  - Navigate SmartMedical pages, wait for elements, extract data
  - Map results to schemas (TimetableResponse, BookingResponse)
  - Avoid logging PII


## Deployment (example via Coolify)
- Deploy next to n8n on the same host and keep the API non-public
- Provide n8n with the internal base URL and API key
- Optionally run with Selenium Grid using SELENIUM_REMOTE_URL


## Testing
Run unit tests locally:
  pytest -q

Tests cover basics: health 200, auth required, 501 placeholders, and simple 429.


## Troubleshooting
- 401: Ensure X-API-Key matches API_KEY in .env or container env.
- 429: Reduce request rate or increase RATE_LIMIT_PER_MIN/RATE_LIMIT_BURST.
- 501: Expected until Selenium logic is implemented.
- 504: Increase REQUEST_TIMEOUT for long operations.
- Chrome/Driver issues: set CHROME_BINARY_PATH/CHROMEDRIVER_PATH or use SELENIUM_REMOTE_URL.


## Roadmap / Future Work
- Implement SmartMedical Selenium logic for timetable scraping and booking
- Add observability (metrics, traces) if needed
- Optionally harden Docker image (non-root, read-only FS)


## Extras
- Interactive API docs (when server is running):
  - http://127.0.0.1:8080/docs (Swagger UI)
  - http://127.0.0.1:8080/redoc (ReDoc)

- Windows Command Prompt (cmd.exe) snippets:
  set API_KEY=change-me
  curl -i -H "X-API-Key: %API_KEY%" http://127.0.0.1:8080/timetable

- Show response headers with curl:
  curl -i http://127.0.0.1:8080/health
