from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.core.config import get_settings
from app.core.exceptions import ErrorCodes
from app.core.schemas import TimetableResponse, ErrorResponse
from app.api.dependencies import principal_id
from app.infrastructure.rate_limit import enforce_rate_limit
from app.smartmedical.scrape_timetable import fetch_timetable

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/timetable",
    response_model=TimetableResponse,
    responses={
        401: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        501: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_timetable(
    pid: str = Depends(principal_id)
):
    enforce_rate_limit(pid)
    s = get_settings()

    try:
        async with asyncio.timeout(s.request_timeout):
            # Enforce credentials presence
            if not (s.smartmedical_username and s.smartmedical_password):
                raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="SmartMedical credentials are not provided (username/password).")

            # Scrape timetable via scraping module (run in a thread to avoid blocking loop)
            resp = await asyncio.to_thread(
                fetch_timetable
            )
            return TimetableResponse(**resp)
    except asyncio.TimeoutError:
        logger.warning("Timetable request timeout", extra={"route": "/timetable", "principal": pid})
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=ErrorCodes.TIMEOUT)
