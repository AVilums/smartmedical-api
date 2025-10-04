from pydantic import BaseModel
from typing import Optional, List


class TimetableResponse(BaseModel):
    doctor: Optional[str] = None
    date: Optional[str] = None
    slots: List[dict] = []
    source: str = "smartmedical"


class BookingRequest(BaseModel):
    date: str
    time: str
    first_name: str
    last_name: str
    phone: str
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    status: str
    booking_id: Optional[str] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
