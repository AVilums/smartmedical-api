from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


class UTF8JSONResponse(JSONResponse):
    # Ensure PowerShell and other clients correctly decode the JSON as UTF-8
    media_type = "application/json; charset=utf-8"

from fastapi.exceptions import RequestValidationError

from app.core.config import get_settings
from app.core.exceptions import ErrorCodes, unhandled_exception_handler, validation_exception_handler
from app.infrastructure.logging_config import configure_logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    s = get_settings()
    logger.info("Service starting", extra={"bind": f"{s.bind_host}:{s.port}", "log_json": s.log_json})
    yield

app = FastAPI(title="SmartMedical Automation Service", version="0.1.0", lifespan=lifespan, default_response_class=UTF8JSONResponse)


# CORS
_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# Ensure a consistent schema for HTTPException to {"error": ...}
@app.exception_handler(HTTPException)
async def http_exception_to_json(request: Request, exc: HTTPException):
    content = {"error": exc.detail if isinstance(exc.detail, str) else ErrorCodes.INTERNAL_ERROR}
    return UTF8JSONResponse(status_code=exc.status_code, content=content)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Cache-Control", "no-store")
    return response


# Routers
from app.api.routes.health import router as health_router  # noqa: E402
from app.api.routes.timetable import router as timetable_router  # noqa: E402
from app.api.routes.booking import router as booking_router  # noqa: E402

app.include_router(health_router)
app.include_router(timetable_router)
app.include_router(booking_router)
