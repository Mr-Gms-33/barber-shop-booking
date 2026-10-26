from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.db import get_db
from app.domain import booking as domain
from app.models import Appointment, AppointmentStatus, Barber, Service
from app.schemas import (
    BookingCreate,
    BookingCreateResult,
    BookingFailed,
    BookingOut,
    RescheduleIn,
    ServiceOut,
    SlotOut,
    StatusLookupIn,
)
from app.services import booking_service as svc
from app.telemetry import BOOKING_DURATION, BOOKINGS_SUBMITTED, tracer

router = APIRouter(prefix="/api", tags=["public"])


@router.get("/services", response_model=list[ServiceOut])
def list_services(db: Session = Depends(get_db)):
    rows = db.scalars(select(Service).where(Service.active.is_(True))).all()
    return rows


@router.get("/barbers")
def list_barbers(db: Session = Depends(get_db)):
    rows = db.scalars(select(Barber).where(Barber.active.is_(True))).all()
    return [{"id": b.id, "name": b.name} for b in rows]


@router.get("/slots", response_model=list[SlotOut])
def available_slots(service_id: int, day: datetime, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if not service or not service.active:
        raise HTTPException(404, "Service not found")
    barbers = list(db.scalars(select(Barber).where(Barber.active.is_(True))))
    from app.models import BarberSchedule

    schedules = list(db.scalars(select(BarberSchedule)))
    schedules_by_barber: dict[int, list] = {}
    for s in schedules:
        schedules_by_barber.setdefault(s.barber_id, []).append(s)
    appointments = svc.load_blocking_appointments(db)
    slots = domain.find_available_slots(
        service, barbers, schedules_by_barber, appointments, day.replace(tzinfo=None)
    )
    out: list[SlotOut] = []
    for bid, start in slots:
        barber = db.get(Barber, bid)
        if barber:
            out.append(SlotOut(barber_id=bid, barber_name=barber.name, start_at=start))
    return out


@router.post("/bookings", response_model=BookingCreateResult | BookingFailed)
def create_booking(body: BookingCreate, db: Session = Depends(get_db)):
    with tracer.start_as_current_span("create_booking") as span:
        span.set_attribute("booking.service_id", body.service_id)
        start = datetime.now(timezone.utc)
        try:
            service = db.get(Service, body.service_id)
            if not service:
                BOOKINGS_SUBMITTED.labels(result="failed").inc()
                return BookingFailed(ok=False, message="Service not found")

            if body.any_barber and body.barber_id is not None:
                BOOKINGS_SUBMITTED.labels(result="failed").inc()
                return BookingFailed(ok=False, message="Choose either a barber or any barber")

            ok, suggestions = svc.validate_slot(
                db, service, body.start_at.replace(tzinfo=None),
                body.barber_id, body.any_barber,
            )
            if not ok:
                BOOKINGS_SUBMITTED.labels(result="failed").inc()
                return BookingFailed(
                    ok=False,
                    message="Selected time is not available",
                    suggestions=suggestions,
                )

            assigned_barber = body.barber_id
            if body.any_barber:
                barbers = list(db.scalars(select(Barber).where(Barber.active.is_(True))))
                end_at = domain.appointment_end(body.start_at.replace(tzinfo=None), service)
                appointments = svc.load_blocking_appointments(db)
                assigned_barber = next(
                    (
                        b.id
                        for b in barbers
                        if domain.barber_is_free(
                            b.id,
                            body.start_at.replace(tzinfo=None),
                            end_at,
                            appointments,
                        )
                    ),
                    None,
                )

            appt = Appointment(
                booking_code=svc.generate_booking_code(),
                guest_name=body.guest_name.strip(),
                guest_phone=body.guest_phone.strip(),
                guest_email=body.guest_email,
                service_id=body.service_id,
                barber_id=assigned_barber,
                any_barber=body.any_barber,
                start_at=body.start_at.replace(tzinfo=None),
                status=AppointmentStatus.pending,
            )
            db.add(appt)
            db.commit()
            db.refresh(appt)
            appt = db.scalar(
                select(Appointment)
                .options(joinedload(Appointment.service), joinedload(Appointment.barber))
                .where(Appointment.id == appt.id)
            )
            BOOKINGS_SUBMITTED.labels(result="success").inc()
            return BookingCreateResult(ok=True, booking=svc.to_booking_out(appt))
        finally:
            BOOKING_DURATION.observe((datetime.now(timezone.utc) - start).total_seconds())


@router.post("/bookings/lookup", response_model=BookingOut)
def lookup_booking(body: StatusLookupIn, db: Session = Depends(get_db)):
    appt = db.scalar(
        select(Appointment)
        .options(joinedload(Appointment.service), joinedload(Appointment.barber))
        .where(Appointment.booking_code == body.booking_code.upper())
    )
    if not appt:
        raise HTTPException(404, "Booking not found")
    phone = appt.guest_phone.replace(" ", "")
    if not phone.endswith(body.phone_last4):
        raise HTTPException(403, "Verification failed")
    return svc.to_booking_out(appt)


@router.post("/bookings/{booking_code}/cancel", response_model=BookingOut)
def cancel_booking(booking_code: str, body: StatusLookupIn, db: Session = Depends(get_db)):
    appt = _verified_appt(db, booking_code, body.phone_last4)
    now = datetime.utcnow()
    if domain.is_within_cutoff(appt.start_at, now, settings.booking_cutoff_hours):
        raise HTTPException(400, "Cannot cancel within 2 hours of appointment")
    if appt.status not in (AppointmentStatus.pending, AppointmentStatus.confirmed):
        raise HTTPException(400, "Cannot cancel this booking")
    appt.status = AppointmentStatus.cancelled
    db.commit()
    db.refresh(appt)
    return svc.to_booking_out(appt)


@router.post("/bookings/{booking_code}/reschedule", response_model=BookingOut)
def reschedule_booking(
    booking_code: str, payload: RescheduleIn, db: Session = Depends(get_db)
):
    appt = _verified_appt(db, booking_code, payload.phone_last4)
    now = datetime.utcnow()
    if domain.is_within_cutoff(appt.start_at, now, settings.booking_cutoff_hours):
        raise HTTPException(400, "Cannot reschedule within 2 hours of appointment")
    if appt.status != AppointmentStatus.confirmed:
        raise HTTPException(400, "Only confirmed bookings can be rescheduled")
    service = appt.service
    ok, suggestions = svc.validate_slot(
        db,
        service,
        payload.start_at.replace(tzinfo=None),
        payload.barber_id,
        payload.any_barber,
        exclude_id=appt.id,
    )
    if not ok:
        raise HTTPException(409, detail={"message": "Slot unavailable", "suggestions": suggestions})
    appt.start_at = payload.start_at.replace(tzinfo=None)
    appt.any_barber = payload.any_barber
    appt.barber_id = payload.barber_id
    appt.status = AppointmentStatus.pending
    db.commit()
    db.refresh(appt)
    return svc.to_booking_out(appt)


def _verified_appt(db: Session, booking_code: str, phone_last4: str) -> Appointment:
    appt = db.scalar(
        select(Appointment)
        .options(joinedload(Appointment.service), joinedload(Appointment.barber))
        .where(Appointment.booking_code == booking_code.upper())
    )
    if not appt:
        raise HTTPException(404, "Booking not found")
    phone = appt.guest_phone.replace(" ", "")
    if not phone.endswith(phone_last4):
        raise HTTPException(403, "Verification failed")
    return appt
