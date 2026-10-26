from datetime import datetime, time, timedelta
from typing import Iterable

from app.models import Appointment, AppointmentStatus, Barber, BarberSchedule, Service

BLOCKING_STATUSES = {AppointmentStatus.pending, AppointmentStatus.confirmed}
SLOT_STEP = timedelta(minutes=15)


def appointment_end(start: datetime, service: Service) -> datetime:
    return start + timedelta(minutes=service.duration_minutes)


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def is_within_cutoff(start_at: datetime, now: datetime, cutoff_hours: int) -> bool:
    """True if start is inside cutoff window (too late to cancel/reschedule)."""
    return start_at - now <= timedelta(hours=cutoff_hours)


def barber_working_window(
    schedules: Iterable[BarberSchedule], day: datetime
) -> list[tuple[datetime, datetime]]:
    dow = day.weekday()
    windows: list[tuple[datetime, datetime]] = []
    for s in schedules:
        if s.day_of_week != dow:
            continue
        start = datetime.combine(day.date(), s.start_time)
        end = datetime.combine(day.date(), s.end_time)
        if start < end:
            windows.append((start, end))
    return windows


def iter_slot_starts(
    window_start: datetime, window_end: datetime, duration_minutes: int
) -> Iterable[datetime]:
    cursor = window_start
    latest_start = window_end - timedelta(minutes=duration_minutes)
    while cursor <= latest_start:
        yield cursor
        cursor += SLOT_STEP


def barber_is_free(
    barber_id: int,
    start: datetime,
    end: datetime,
    appointments: Iterable[Appointment],
    exclude_id: int | None = None,
) -> bool:
    for appt in appointments:
        if appt.id == exclude_id:
            continue
        if appt.barber_id != barber_id:
            continue
        if appt.status not in BLOCKING_STATUSES:
            continue
        if appt.service:
            appt_end = appointment_end(appt.start_at, appt.service)
        else:
            appt_end = appt.start_at + timedelta(minutes=30)
        if overlaps(start, end, appt.start_at, appt_end):
            return False
    return True


def find_available_slots(
    service: Service,
    barbers: list[Barber],
    schedules_by_barber: dict[int, list[BarberSchedule]],
    appointments: list[Appointment],
    day: datetime,
    limit: int = 20,
) -> list[tuple[int, datetime]]:
    """Return (barber_id, start) slots sorted by time."""
    duration = service.duration_minutes
    slots: list[tuple[int, datetime]] = []
    for barber in barbers:
        if not barber.active:
            continue
        for w_start, w_end in barber_working_window(schedules_by_barber.get(barber.id, []), day):
            for slot_start in iter_slot_starts(w_start, w_end, duration):
                slot_end = slot_start + timedelta(minutes=duration)
                if barber_is_free(barber.id, slot_start, slot_end, appointments):
                    slots.append((barber.id, slot_start))
    slots.sort(key=lambda x: x[1])
    return slots[:limit]


def suggest_alternatives(
    service: Service,
    barbers: list[Barber],
    schedules_by_barber: dict[int, list[BarberSchedule]],
    appointments: list[Appointment],
    preferred_barber_id: int | None,
    preferred_start: datetime,
    limit: int = 8,
) -> list[tuple[int, datetime]]:
    """Nearby times for same barber, then other barbers near preferred time."""
    duration = service.duration_minutes
    end = preferred_start + timedelta(minutes=duration)
    suggestions: list[tuple[int, datetime]] = []
    day = preferred_start

    if preferred_barber_id is not None:
        for offset_days in range(0, 7):
            d = day + timedelta(days=offset_days)
            for bid, start in find_available_slots(
                service, [b for b in barbers if b.id == preferred_barber_id],
                schedules_by_barber, appointments, d, limit=50
            ):
                if start != preferred_start:
                    suggestions.append((bid, start))
            if len(suggestions) >= limit:
                break

    if len(suggestions) < limit:
        for offset_days in range(0, 7):
            d = day + timedelta(days=offset_days)
            for bid, start in find_available_slots(
                service, barbers, schedules_by_barber, appointments, d, limit=50
            ):
                if preferred_barber_id and bid == preferred_barber_id:
                    continue
                if abs((start - preferred_start).total_seconds()) <= 3600 * 3:
                    suggestions.append((bid, start))
            if len(suggestions) >= limit:
                break

    seen: set[tuple[int, datetime]] = set()
    unique: list[tuple[int, datetime]] = []
    for item in sorted(suggestions, key=lambda x: abs((x[1] - preferred_start).total_seconds())):
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
        if len(unique) >= limit:
            break
    return unique


def can_transition(status: AppointmentStatus, action: str) -> bool:
    rules = {
        ("pending", "accept"): True,
        ("pending", "reject"): True,
        ("pending", "cancel"): True,
        ("confirmed", "checkout"): True,
        ("confirmed", "cancel"): True,
        ("confirmed", "reschedule"): True,
    }
    return rules.get((status.value, action), False)
