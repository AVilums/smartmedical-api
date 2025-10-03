from __future__ import annotations

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.core.config import get_settings
from app.core.exceptions import ErrorCodes
from app.core.schemas import BookingRequest, BookingResponse, ErrorResponse
from app.api.dependencies import principal_id
from app.infrastructure.rate_limit import enforce_rate_limit
from app.infrastructure.selenium_client import SmartMedicalClient

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/book",
    response_model=BookingResponse,
    responses={
        401: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        501: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def book(
    payload: BookingRequest,
    pid: str = Depends(principal_id),
):
    enforce_rate_limit(pid)
    s = get_settings()

    try:
        async with asyncio.timeout(s.request_timeout):
            client = SmartMedicalClient()
            _ = client.book(booking_payload=payload.model_dump())
            return BookingResponse(status="success", booking_id="TBD", message="Booking complete")
    except NotImplementedError as exc:
        logger.info("Booking not implemented", extra={"route": "/book", "principal": pid})
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(exc))
    except asyncio.TimeoutError:
        logger.warning("Booking request timeout", extra={"route": "/book", "principal": pid})
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=ErrorCodes.TIMEOUT)
