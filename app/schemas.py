
from pydantic import BaseModel


class TimetableRequest(BaseModel):
    doctor: str = None
    date: str = None


class TimeSlot(BaseModel):
    time: str
    available: bool = True


class TimetableResponse(BaseModel):
    doctor: str = None
    date: str = None
    slots: list = []
    source: str = "smartmedical"


class PatientInfo(BaseModel):
    first_name: str
    last_name: str
    phone: str = None
    email: str = None
    personal_code: str = None


class BookingRequest(BaseModel):
    doctor: str
    date: str
    time: str
    patient: PatientInfo
    notes: str = None


class BookingResponse(BaseModel):
    status: str
    booking_id: str = None
    message: str = None


class ErrorResponse(BaseModel):
    error: str
    detail: str = None