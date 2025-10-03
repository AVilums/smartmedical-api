from pydantic import BaseModel
from typing import Optional, List


class TimetableRequest(BaseModel):
    doctor: Optional[str] = None
    date: Optional[str] = None


class TimeSlot(BaseModel):
    time: str
    available: bool = True


class TimetableResponse(BaseModel):
    doctor: Optional[str] = None
    date: Optional[str] = None
    slots: List[dict] = []
    source: str = "smartmedical"


class PatientInfo(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    personal_code: Optional[str] = None


class BookingRequest(BaseModel):
    doctor: str
    date: str
    time: str
    patient: PatientInfo
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    status: str
    booking_id: Optional[str] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
