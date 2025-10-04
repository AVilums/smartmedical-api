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
from app.smartmedical.create_booking import create_booking as sm_create_booking

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

    # Enforce credentials presence
    if not (s.smartmedical_username and s.smartmedical_password):
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="SmartMedical credentials are not provided (username/password).")

    try:
        async with asyncio.timeout(s.request_timeout):
            result = await asyncio.to_thread(
                sm_create_booking,
                date=payload.date,
                time=payload.time,
                first_name=payload.first_name,
                last_name=payload.last_name,
                phone=payload.phone,
                notes=payload.notes,
            )
            return BookingResponse(**result)
    except asyncio.TimeoutError:
        logger.exception("Booking request timeout", extra={"route": "/book", "principal": pid})
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=ErrorCodes.TIMEOUT)
    except HTTPException:
        logger.exception("Booking failed due to HTTP error", extra={"route": "/book", "principal": pid})
        raise
    except Exception as e:
        logger.exception(f"Booking failed due to unexpected error {e}", extra={"route": "/book", "principal": pid})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ErrorCodes.INTERNAL_ERROR)
