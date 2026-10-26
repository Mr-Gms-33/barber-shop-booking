"""QA acceptance tests mapped to GitHub issues #1–#22."""

from datetime import datetime, time, timedelta

import pytest
from sqlalchemy.orm import Session

from app.models import Appointment, AppointmentStatus, Barber, BarberSchedule, Service


def admin_headers(client):
    r = client.post("/api/admin/login", json={"username": "admin", "password": "changeme"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def book(client, service_id, barber_id, start_at, phone="5559990001"):
    return client.post(
        "/api/bookings",
        json={
            "service_id": service_id,
            "start_at": start_at.isoformat(),
            "barber_id": barber_id,
            "any_barber": False,
            "guest_name": "Guest",
            "guest_phone": phone,
        },
    )


def test_admin_service_crud(client, db_session: Session):
    h = admin_headers(client)
    created = client.post(
        "/api/admin/services",
        headers=h,
        json={"name": "Test Cut", "duration_minutes": 20, "price": 19.99, "active": True},
    )
    assert created.status_code == 200
    sid = created.json()["id"]
    patched = client.patch(
        f"/api/admin/services/{sid}",
        headers=h,
        json={"name": "Test Cut Updated", "duration_minutes": 25, "price": 21, "active": False},
    )
    assert patched.status_code == 200
    assert patched.json()["active"] is False
    public = client.get("/api/services").json()
    assert all(s["id"] != sid for s in public)


def test_admin_barber_crud(client, db_session: Session):
    h = admin_headers(client)
    created = client.post("/api/admin/barbers", headers=h, json={"name": "New Barber", "active": True})
    assert created.status_code == 200
    bid = created.json()["id"]
    client.patch(f"/api/admin/barbers/{bid}", headers=h, json={"name": "New Barber", "active": False})
    public = client.get("/api/barbers").json()
    assert all(b["id"] != bid for b in public)


def test_weekly_schedule(client, db_session: Session):
    h = admin_headers(client)
    barber = db_session.query(Barber).first()
    sched = client.put(
        f"/api/admin/barbers/{barber.id}/schedule",
        headers=h,
        json=[{"day_of_week": 0, "start_time": "10:00:00", "end_time": "16:00:00"}],
    )
    assert sched.status_code == 200
    assert len(sched.json()) == 1


def test_double_booking_prevented(client, db_session, next_weekday_10am):
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    r1 = book(client, svc.id, barber.id, next_weekday_10am)
    assert r1.json()["ok"] is True
    r2 = book(client, svc.id, barber.id, next_weekday_10am, phone="5559990002")
    data = r2.json()
    assert data["ok"] is False


def test_pending_blocks_slot(client, db_session, next_weekday_10am):
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    book(client, svc.id, barber.id, next_weekday_10am)
    r2 = book(client, svc.id, barber.id, next_weekday_10am, phone="5559990003")
    assert r2.json()["ok"] is False


def test_guest_booking_pending_and_lookup(client, db_session, next_weekday_10am):
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    r = book(client, svc.id, barber.id, next_weekday_10am)
    body = r.json()
    assert body["ok"] is True
    assert body["booking"]["status"] == "pending"
    code = body["booking"]["booking_code"]
    lookup = client.post(
        "/api/bookings/lookup",
        json={"booking_code": code, "phone_last4": "0001"},
    )
    assert lookup.status_code == 200


def test_suggestions_when_invalid(client, db_session, next_weekday_10am):
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    book(client, svc.id, barber.id, next_weekday_10am)
    r = book(client, svc.id, barber.id, next_weekday_10am, phone="5559990004")
    data = r.json()
    assert data["ok"] is False
    assert "suggestions" in data


def test_cancel_outside_cutoff(client, db_session):
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    start = datetime.utcnow() + timedelta(days=3)
    start = start.replace(hour=10, minute=0, second=0, microsecond=0)
    while start.weekday() >= 5:
        start += timedelta(days=1)
    r = book(client, svc.id, barber.id, start)
    code = r.json()["booking"]["booking_code"]
    cancel = client.post(
        f"/api/bookings/{code}/cancel",
        json={"booking_code": code, "phone_last4": "0001"},
    )
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"


def test_cancel_inside_cutoff_fails(client, db_session):
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    start = datetime.utcnow() + timedelta(hours=1)
    r = book(client, svc.id, barber.id, start, phone="5551112222")
    code = r.json()["booking"]["booking_code"]
    cancel = client.post(
        f"/api/bookings/{code}/cancel",
        json={"booking_code": code, "phone_last4": "2222"},
    )
    assert cancel.status_code == 400


def test_accept_reject_and_any_barber(client, db_session, next_weekday_10am):
    h = admin_headers(client)
    svc = db_session.query(Service).first()
    r = client.post(
        "/api/bookings",
        json={
            "service_id": svc.id,
            "start_at": next_weekday_10am.isoformat(),
            "any_barber": True,
            "guest_name": "Any",
            "guest_phone": "5550003333",
        },
    )
    assert r.json()["ok"] is True
    appt_id = r.json()["booking"]["id"]
    fail = client.post(f"/api/admin/appointments/{appt_id}/accept", headers=h, json={})
    assert fail.status_code == 400
    barber = db_session.query(Barber).first()
    ok = client.post(
        f"/api/admin/appointments/{appt_id}/accept", headers=h, json={"barber_id": barber.id}
    )
    assert ok.status_code == 200

    r2 = book(client, svc.id, barber.id, next_weekday_10am + timedelta(hours=2), phone="5550004444")
    appt2 = r2.json()["booking"]["id"]
    client.post(f"/api/admin/appointments/{appt2}/reject", headers=h)
    st = client.post(
        "/api/bookings/lookup", json={"booking_code": r2.json()["booking"]["booking_code"], "phone_last4": "4444"}
    )
    assert st.json()["status"] == "declined"


def test_reschedule_returns_pending(client, db_session, next_weekday_10am):
    h = admin_headers(client)
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    r = book(client, svc.id, barber.id, next_weekday_10am, phone="5550005555")
    code = r.json()["booking"]["booking_code"]
    appt_id = r.json()["booking"]["id"]
    client.post(f"/api/admin/appointments/{appt_id}/accept", headers=h, json={})
    new_start = next_weekday_10am + timedelta(hours=3)
    res = client.post(
        f"/api/bookings/{code}/reschedule",
        json={
            "booking_code": code,
            "phone_last4": "5555",
            "start_at": new_start.isoformat(),
            "barber_id": barber.id,
            "any_barber": False,
        },
    )
    assert res.status_code == 200
    assert res.json()["status"] == "pending"


def test_history_and_dashboard(client, db_session, next_weekday_10am):
    h = admin_headers(client)
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    r = book(client, svc.id, barber.id, next_weekday_10am, phone="5550006666")
    appt_id = r.json()["booking"]["id"]
    client.post(f"/api/admin/appointments/{appt_id}/accept", headers=h, json={})
    client.post(f"/api/admin/appointments/{appt_id}/checkout", headers=h, json={"revenue": 30})
    hist = client.get("/api/admin/appointments?status=completed", headers=h)
    assert hist.status_code == 200
    assert len(hist.json()) >= 1
    from_d = (next_weekday_10am - timedelta(days=1)).isoformat()
    to_d = (next_weekday_10am + timedelta(days=1)).isoformat()
    dash = client.get(f"/api/admin/dashboard?from_date={from_d}&to_date={to_d}", headers=h)
    d = dash.json()
    assert d["total_revenue"] >= 30
    assert len(d["by_service"]) >= 1
    assert len(d["by_barber"]) >= 1
    assert len(d["by_day"]) >= 1


def test_checkout_adjusted_revenue(client, db_session, next_weekday_10am):
    h = admin_headers(client)
    svc = db_session.query(Service).first()
    barber = db_session.query(Barber).first()
    r = book(client, svc.id, barber.id, next_weekday_10am, phone="5550007777")
    appt_id = r.json()["booking"]["id"]
    client.post(f"/api/admin/appointments/{appt_id}/accept", headers=h, json={})
    co = client.post(f"/api/admin/appointments/{appt_id}/checkout", headers=h, json={"revenue": 99.5})
    assert co.status_code == 200
