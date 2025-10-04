from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette import status


class ErrorCodes:
    UNAUTHORIZED = "unauthorized"
    RATE_LIMITED = "rate_limited"
    BAD_REQUEST = "bad_request"
    NOT_IMPLEMENTED = "not_implemented"
    INTERNAL_ERROR = "internal_error"
    TIMEOUT = "timeout"


def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": ErrorCodes.BAD_REQUEST,
            "detail": exc.errors(),
        },
    )


def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": ErrorCodes.INTERNAL_ERROR,
            "detail": "An unexpected error occurred",
        },
    )
