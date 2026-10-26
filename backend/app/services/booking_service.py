import secrets
import string
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.domain import booking as domain
from app.models import Appointment, AppointmentStatus, Barber, BarberSchedule, Service
from app.schemas import BookingOut, SuggestionOut


def generate_booking_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


def to_booking_out(appt: Appointment) -> BookingOut:
    return BookingOut(
        id=appt.id,
        booking_code=appt.booking_code,
        guest_name=appt.guest_name,
        guest_phone=appt.guest_phone,
        guest_email=appt.guest_email,
        service_id=appt.service_id,
        service_name=appt.service.name if appt.service else "",
        barber_id=appt.barber_id,
        barber_name=appt.barber.name if appt.barber else None,
        any_barber=appt.any_barber,
        start_at=appt.start_at,
        status=appt.status,
        revenue=float(appt.revenue) if appt.revenue is not None else None,
    )


def load_blocking_appointments(db: Session) -> list[Appointment]:
    q = (
        select(Appointment)
        .options(joinedload(Appointment.service))
        .where(Appointment.status.in_(list(domain.BLOCKING_STATUSES)))
    )
    return list(db.scalars(q).all())


def validate_slot(
    db: Session,
    service: Service,
    start_at: datetime,
    barber_id: int | None,
    any_barber: bool,
    exclude_id: int | None = None,
) -> tuple[bool, list[SuggestionOut]]:
    if not service.active:
        return False, []
    barbers = list(db.scalars(select(Barber).where(Barber.active.is_(True))))
    schedules = list(db.scalars(select(BarberSchedule)))
    schedules_by_barber: dict[int, list[BarberSchedule]] = {}
    for s in schedules:
        schedules_by_barber.setdefault(s.barber_id, []).append(s)
    appointments = load_blocking_appointments(db)
    end_at = domain.appointment_end(start_at, service)

    if any_barber:
        for b in barbers:
            if domain.barber_is_free(b.id, start_at, end_at, appointments, exclude_id):
                return True, []
        alts = domain.suggest_alternatives(
            service, barbers, schedules_by_barber, appointments, None, start_at
        )
        return False, _suggestions(db, alts)

    if barber_id is None:
        return False, []

    barber = db.get(Barber, barber_id)
    if not barber or not barber.active:
        return False, []

    if domain.barber_is_free(barber_id, start_at, end_at, appointments, exclude_id):
        return True, []

    alts = domain.suggest_alternatives(
        service, barbers, schedules_by_barber, appointments, barber_id, start_at
    )
    return False, _suggestions(db, alts)


def _suggestions(db: Session, alts: list[tuple[int, datetime]]) -> list[SuggestionOut]:
    out: list[SuggestionOut] = []
    for bid, start in alts:
        barber = db.get(Barber, bid)
        if barber:
            out.append(
                SuggestionOut(barber_id=bid, barber_name=barber.name, start_at=start)
            )
    return out


def dashboard_stats(db: Session, start: datetime, end: datetime) -> dict:
    q = (
        select(Appointment)
        .options(joinedload(Appointment.service), joinedload(Appointment.barber))
        .where(
            Appointment.status == AppointmentStatus.completed,
            Appointment.start_at >= start,
            Appointment.start_at <= end,
        )
    )
    appts = list(db.scalars(q).all())
    total = sum(float(a.revenue or 0) for a in appts)

    by_service: dict[str, float] = {}
    by_barber: dict[str, float] = {}
    by_day: dict[str, float] = {}
    for a in appts:
        rev = float(a.revenue or 0)
        by_service[a.service.name] = by_service.get(a.service.name, 0) + rev
        bname = a.barber.name if a.barber else "Unassigned"
        by_barber[bname] = by_barber.get(bname, 0) + rev
        day = a.start_at.date().isoformat()
        by_day[day] = by_day.get(day, 0) + rev

    return {
        "total_revenue": total,
        "by_service": [{"name": k, "revenue": v} for k, v in sorted(by_service.items())],
        "by_barber": [{"name": k, "revenue": v} for k, v in sorted(by_barber.items())],
        "by_day": [{"date": k, "revenue": v} for k, v in sorted(by_day.items())],
    }
