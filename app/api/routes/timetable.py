from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from starlette import status

from app.core.config import get_settings
from app.core.exceptions import ErrorCodes
from app.core.schemas import TimetableResponse, ErrorResponse
from app.api.dependencies import principal_id
from app.infrastructure.rate_limit import enforce_rate_limit
from app.smartmedical.auth import login as sm_login
from app.smartmedical.scraping import fetch_timetable

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
    request: Request,
    doctor: Optional[str] = Query(default=None),
    date_param: Optional[date] = Query(default=None, alias="date"),
    pid: str = Depends(principal_id),
):
    enforce_rate_limit(pid)
    s = get_settings()

    try:
        async with asyncio.timeout(s.request_timeout):
            # Conditional login before requesting timetable
            if getattr(s, "smartmedical_login_on_timetable", False) and s.smartmedical_username and s.smartmedical_password:
                try:
                    # Run blocking Selenium login in a thread to avoid blocking the event loop
                    await asyncio.to_thread(sm_login)
                    logger.info("SmartMedical login attempted before timetable", extra={"route": "/timetable", "principal": pid})
                except Exception as e:
                    logger.warning("SmartMedical login failed/skipped", extra={"route": "/timetable", "principal": pid, "error": str(e)})
            # Fetch timetable via scraping module (runs in a thread to avoid blocking loop)
            resp = await asyncio.to_thread(
                fetch_timetable,
                doctor=doctor,
                date_str=(date_param.isoformat() if date_param else None),
            )
            return TimetableResponse(**resp)
    except NotImplementedError as exc:
        logger.info(
            "Timetable not implemented",
            extra={"route": "/timetable", "principal": pid, "doctor": doctor, "date": str(date_param) if date_param else None},
        )
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(exc))
    except asyncio.TimeoutError:
        logger.warning("Timetable request timeout", extra={"route": "/timetable", "principal": pid})
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=ErrorCodes.TIMEOUT)
