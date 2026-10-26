from datetime import datetime, timedelta

from app.domain.booking import is_within_cutoff, overlaps
from app.models import AppointmentStatus
from app.domain.booking import can_transition


def test_overlaps():
    a0 = datetime(2026, 1, 1, 10, 0)
    a1 = datetime(2026, 1, 1, 11, 0)
    b0 = datetime(2026, 1, 1, 10, 30)
    b1 = datetime(2026, 1, 1, 11, 30)
    assert overlaps(a0, a1, b0, b1)


def test_cutoff():
    start = datetime.utcnow() + timedelta(hours=1)
    now = datetime.utcnow()
    assert is_within_cutoff(start, now, 2) is True


def test_transitions():
    assert can_transition(AppointmentStatus.pending, "accept")
    assert not can_transition(AppointmentStatus.declined, "accept")
