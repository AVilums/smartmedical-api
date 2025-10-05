# SmartMedical Booking API

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com)
[![Selenium](https://img.shields.io/badge/Selenium-4.24.0-43B02A.svg)](https://selenium.dev)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

The SmartMedical Booking API automates interactions with medical booking systems by providing a RESTful interface. It uses Selenium WebDriver to navigate through web interfaces and perform booking operations programmatically.

### Key Components:
- **FastAPI Web Framework**: High-performance API with automatic documentation
- **Selenium Automation**: Browser automation for web scraping and form submission
- **Docker Containerization**: Easy deployment and development environment
- **Rate Limiting**: Built-in request throttling for stability
- **Comprehensive Logging**: Detailed logging with PII protection

## Features

- **Timetable Retrieval**: Fetch available appointment slots `/timetable`
- **Booking Creation**: Automate appointment booking process `/book`
- **API Key Authentication**: Secure access control
- **Rate Limiting**: Protection against abuse
- **Docker Support**: Containerized deployment
- **Health Checks**: Service monitoring endpoints
- **Comprehensive Logging**: Request tracking and debugging
- **CORS Support**: Cross-origin resource sharing

## Architecture

```
smartmedical-api/
├── app/
│   ├── api/                    # FastAPI application layer
│   │   ├── routes/            # API route definitions
│   │   ├── dependencies.py    # Dependency injection
│   │   └── app.py            # FastAPI app configuration
│   ├── core/                  # Core business logic
│   │   ├── config.py         # Configuration management
│   │   ├── schemas.py        # Pydantic models
│   │   └── exceptions.py     # Custom exceptions
│   ├── smartmedical/         # Domain-specific automation
│   │   ├── auth.py          # Authentication logic
│   │   ├── navigation.py    # Web navigation
│   │   ├── scrape_timetable.py # Timetable scraping
│   │   └── create_booking.py   # Booking automation
│   ├── infrastructure/       # Infrastructure concerns
│   │   ├── logging_config.py # Logging configuration
│   │   └── rate_limit.py    # Rate limiting implementation
│   └── main.py              # Application entry point
├── tests/                    # Test suite
├── docker-compose.yml       # Docker services configuration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── README.md              # Basic usage guide
```


## Prerequisites

- **Python**: 3.11 or higher
- **Docker**: 20.10 or higher (recommended)
- **Docker Compose**: 2.0 or higher
- **Chrome/Chromium**: For Selenium automation (handled by Docker)

## Installation

### Option 1: Docker (Recommended)

1. **Clone the repository:**
```shell script
git clone <repository-url>
cd smartmedical-api
```


2. **Configure environment:**
```shell script
cp .env.example .env
# Edit .env with your configuration
```


3. **Build and start services:**
```shell script
docker compose build
docker compose up -d
```


4. **Verify installation:**
```shell script
docker compose ps
curl http://localhost:8080/health
```


### Option 2: Local Development

1. **Set up virtual environment:**
```shell script
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


2. **Install dependencies:**
```shell script
pip install -r requirements.txt
```


3. **Configure environment:**
```shell script
cp .env.example .env
# Edit .env for local development
```


4. **Run the application:**
```shell script
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```


## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | Authentication key | `dev-api-key` | Yes |
| `BIND_HOST` | Server bind address | `127.0.0.1` | No |
| `PORT` | Server port | `8080` | No |
| `RATE_LIMIT_PER_MIN` | Requests per minute | `30` | No |
| `RATE_LIMIT_BURST` | Burst limit | `60` | No |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | `60` | No |
| `SELENIUM_PAGELOAD_TIMEOUT` | Page load timeout | `30` | No |
| `SELENIUM_IMPLICIT_WAIT` | Implicit wait time | `5` | No |
| `SELENIUM_REMOTE_URL` | Selenium Grid URL | `http://selenium:4444/wd/hub` | No |
| `SMARTMEDICAL_USERNAME` | SmartMedical username | - | Yes |
| `SMARTMEDICAL_PASSWORD` | SmartMedical password | - | Yes |
| `BROWSER` | Browser type | `headless-chrome` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Docker Services

- **web**: Main FastAPI application (port 8080)
- **selenium**: Standalone Chrome for automation (port 4444)

## Usage

### Health Check

```shell script
curl -H "x-api-key: dev-api-key" http://localhost:8080/health
```


### Retrieve Timetable

**PowerShell:**
```textmate
Invoke-RestMethod -Method Get -Uri "http://localhost:8080/timetable" -Headers @{"x-api-key"="dev-api-key"} | ConvertTo-Json -Depth 10
```


**cURL:**
```shell script
curl -H "x-api-key: dev-api-key" http://localhost:8080/timetable
```


### Create Booking

**PowerShell:**
```textmate
$Body = @{
    date = "2025-10-10"
    time = "12:00"
    first_name = "Test"
    last_name = "User"
    phone = "+37100000000"
    notes = "API booking"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "http://localhost:8080/book" -Headers @{"x-api-key"="dev-api-key"} -Body $Body -ContentType "application/json"
```


**cURL:**
```shell script
curl -X POST http://localhost:8080/book \
  -H "x-api-key: dev-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-10-10",
    "time": "12:00",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+37100000000",
    "notes": "API booking"
  }'
```


## API Documentation

### Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/health` | GET | Service health check | Required |
| `/timetable` | GET | Retrieve available slots | Required |
| `/book` | POST | Create new booking | Required |

### Authentication

All endpoints require an `x-api-key` header:

```
x-api-key: your-api-key-here
```


### Response Formats

**Success Response:**
```json
{
  "status": "success",
  "data": {  },
  "message": "Operation completed successfully"
}
```


**Error Response:**
```json
{
  "status": "error",
  "error_code": "ERROR_CODE",
  "message": "Error description",
  "details": {  }
}
```


### Interactive Documentation

When running locally, visit:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Development

### Project Structure

The project follows Clean Architecture principles:

- **API Layer**: FastAPI routes and dependencies
- **Core Layer**: Business logic and domain models
- **Infrastructure Layer**: External services and utilities
- **Domain Layer**: SmartMedical-specific automation

### Code Style

- **Python**: PEP 8 compliant
- **Type Hints**: Full type annotation support
- **Async/Await**: Asynchronous programming patterns

### Adding New Features

1. Define schemas in `app/core/schemas.py`
2. Implement business logic in appropriate domain modules
3. Create API routes in `app/api/routes/`
4. Add configuration options to `app/core/config.py`
5. Write tests in `tests/`

## Testing

### Test Structure

Tests are organized with pytest and include:

- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **Local Tests**: Tests requiring browser/credentials (excluded from CI)

### Running Tests

```shell script
# All tests
pytest

# Exclude local tests (CI-safe)
pytest -m "not local"

# Verbose output
pytest -v

# With coverage
pytest --cov=app
```


### Test Markers

- `@pytest.mark.local`: Tests requiring local environment setup

## Deployment

### Docker Deployment (Production)

1. **Create production environment file:**
```shell script
cp .env.example .env.prod
# Configure production values
```


2. **Build production image:**
```shell script
docker compose -f docker-compose.yml build
```


3. **Deploy with production config:**
```shell script
docker compose --env-file .env.prod up -d
```


### Kubernetes Deployment

Example deployment manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smartmedical-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smartmedical-api
  template:
    metadata:
      labels:
        app: smartmedical-api
    spec:
      containers:
      - name: api
        image: smartmedical-api:latest
        ports:
        - containerPort: 8080
        envFrom:
        - secretRef:
            name: smartmedical-secrets
```


## Troubleshooting

### Common Issues

**1. Selenium Connection Failed**
```
Solution: Ensure selenium service is running
docker compose ps
docker compose logs selenium
```


**2. Authentication Errors**
```
Solution: Verify credentials in .env file
Check SMARTMEDICAL_USERNAME and SMARTMEDICAL_PASSWORD
```


**3. Rate Limiting**
```
Solution: Adjust rate limits or implement backoff
Modify RATE_LIMIT_PER_MIN in configuration
```


**4. Timeout Issues**
```
Solution: Increase timeout values
Adjust SELENIUM_PAGELOAD_TIMEOUT and REQUEST_TIMEOUT
```


### Debugging

Enable debug logging:
```shell script
export LOG_LEVEL=DEBUG
```


View application logs:
```shell script
docker compose logs -f web
```


### Development Guidelines

- Write tests for new features
- Follow existing code patterns
- Update documentation
- Ensure CI passes

## License

This project is licensed under the GPL-3.0 license - see the LICENSE file for details.

---