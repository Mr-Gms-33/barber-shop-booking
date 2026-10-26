from datetime import datetime, time
from typing import Literal

from pydantic import BaseModel, Field

from app.models import AppointmentStatus


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    username: str
    password: str


class ServiceIn(BaseModel):
    name: str
    duration_minutes: int = Field(gt=0, le=480)
    price: float = Field(gt=0)
    active: bool = True


class ServiceOut(ServiceIn):
    id: int

    model_config = {"from_attributes": True}


class BarberIn(BaseModel):
    name: str
    active: bool = True


class BarberOut(BarberIn):
    id: int

    model_config = {"from_attributes": True}


class ScheduleIn(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time


class ScheduleOut(ScheduleIn):
    id: int
    barber_id: int

    model_config = {"from_attributes": True}


class SlotOut(BaseModel):
    barber_id: int
    barber_name: str
    start_at: datetime


class SuggestionOut(BaseModel):
    barber_id: int
    barber_name: str
    start_at: datetime


class BookingCreate(BaseModel):
    service_id: int
    start_at: datetime
    barber_id: int | None = None
    any_barber: bool = False
    guest_name: str
    guest_phone: str
    guest_email: str | None = None


class BookingOut(BaseModel):
    id: int
    booking_code: str
    guest_name: str
    guest_phone: str
    guest_email: str | None
    service_id: int
    service_name: str
    barber_id: int | None
    barber_name: str | None
    any_barber: bool
    start_at: datetime
    status: AppointmentStatus
    revenue: float | None

    model_config = {"from_attributes": True}


class BookingCreateResult(BaseModel):
    ok: Literal[True]
    booking: BookingOut


class BookingFailed(BaseModel):
    ok: Literal[False]
    message: str
    suggestions: list[SuggestionOut] = []


class StatusLookupIn(BaseModel):
    booking_code: str
    phone_last4: str


class RescheduleIn(BaseModel):
    booking_code: str
    phone_last4: str
    start_at: datetime
    barber_id: int | None = None
    any_barber: bool = False


class AcceptIn(BaseModel):
    barber_id: int | None = None


class CheckoutIn(BaseModel):
    revenue: float = Field(gt=0)


class DashboardOut(BaseModel):
    total_revenue: float
    by_service: list[dict]
    by_barber: list[dict]
    by_day: list[dict]
