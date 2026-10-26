from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.auth import create_access_token, require_admin, verify_admin
from app.db import get_db
from app.domain import booking as domain
from app.models import Appointment, AppointmentStatus, Barber, BarberSchedule, Service
from app.schemas import (
    AcceptIn,
    BarberIn,
    BarberOut,
    CheckoutIn,
    DashboardOut,
    LoginIn,
    ScheduleIn,
    ScheduleOut,
    ServiceIn,
    ServiceOut,
    TokenOut,
)
from app.services import booking_service as svc

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn):
    if not verify_admin(body.username, body.password):
        raise HTTPException(401, "Invalid credentials")
    return TokenOut(access_token=create_access_token(body.username))


@router.get("/services", response_model=list[ServiceOut])
def admin_list_services(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return list(db.scalars(select(Service)).all())


@router.post("/services", response_model=ServiceOut)
def create_service(body: ServiceIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    row = Service(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/services/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: int, body: ServiceIn, db: Session = Depends(get_db), _: str = Depends(require_admin)
):
    row = db.get(Service, service_id)
    if not row:
        raise HTTPException(404, "Not found")
    for k, v in body.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.get("/barbers", response_model=list[BarberOut])
def admin_list_barbers(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    return list(db.scalars(select(Barber)).all())


@router.post("/barbers", response_model=BarberOut)
def create_barber(body: BarberIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    row = Barber(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/barbers/{barber_id}", response_model=BarberOut)
def update_barber(
    barber_id: int, body: BarberIn, db: Session = Depends(get_db), _: str = Depends(require_admin)
):
    row = db.get(Barber, barber_id)
    if not row:
        raise HTTPException(404, "Not found")
    for k, v in body.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.get("/barbers/{barber_id}/schedule", response_model=list[ScheduleOut])
def get_schedule(barber_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    rows = db.scalars(select(BarberSchedule).where(BarberSchedule.barber_id == barber_id))
    return list(rows)


@router.put("/barbers/{barber_id}/schedule", response_model=list[ScheduleOut])
def set_schedule(
    barber_id: int,
    items: list[ScheduleIn],
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    if not db.get(Barber, barber_id):
        raise HTTPException(404, "Barber not found")
    existing = db.scalars(select(BarberSchedule).where(BarberSchedule.barber_id == barber_id))
    for row in existing:
        db.delete(row)
    created: list[BarberSchedule] = []
    for item in items:
        row = BarberSchedule(barber_id=barber_id, **item.model_dump())
        db.add(row)
        created.append(row)
    db.commit()
    for row in created:
        db.refresh(row)
    return created


@router.get("/appointments/pending", response_model=list)
def pending_appointments(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    rows = db.scalars(
        select(Appointment)
        .options(joinedload(Appointment.service), joinedload(Appointment.barber))
        .where(Appointment.status == AppointmentStatus.pending)
        .order_by(Appointment.start_at)
    )
    return [svc.to_booking_out(a) for a in rows]


@router.get("/appointments", response_model=list)
def list_appointments(
    status: AppointmentStatus | None = None,
    barber_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    q = select(Appointment).options(
        joinedload(Appointment.service), joinedload(Appointment.barber)
    )
    if status:
        q = q.where(Appointment.status == status)
    if barber_id:
        q = q.where(Appointment.barber_id == barber_id)
    if from_date:
        q = q.where(Appointment.start_at >= from_date)
    if to_date:
        q = q.where(Appointment.start_at <= to_date)
    q = q.order_by(Appointment.start_at.desc())
    rows = db.scalars(q)
    return [svc.to_booking_out(a) for a in rows]


@router.post("/appointments/{appt_id}/accept", response_model=dict)
def accept_appointment(
    appt_id: int, body: AcceptIn, db: Session = Depends(get_db), _: str = Depends(require_admin)
):
    appt = db.scalar(
        select(Appointment)
        .options(joinedload(Appointment.service))
        .where(Appointment.id == appt_id)
    )
    if not appt or appt.status != AppointmentStatus.pending:
        raise HTTPException(400, "Invalid appointment")
    if appt.any_barber:
        if not body.barber_id:
            raise HTTPException(400, "Select a barber when customer chose any barber")
        appt.barber_id = body.barber_id
    elif appt.barber_id is None:
        raise HTTPException(400, "Barber missing")
    ok, _ = svc.validate_slot(
        db, appt.service, appt.start_at, appt.barber_id, False, exclude_id=appt.id
    )
    if not ok:
        raise HTTPException(409, "Slot no longer available")
    appt.status = AppointmentStatus.confirmed
    db.commit()
    return {"status": "confirmed"}


@router.post("/appointments/{appt_id}/reject")
def reject_appointment(appt_id: int, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    appt = db.get(Appointment, appt_id)
    if not appt or appt.status != AppointmentStatus.pending:
        raise HTTPException(400, "Invalid appointment")
    appt.status = AppointmentStatus.declined
    db.commit()
    return {"status": "declined"}


@router.post("/appointments/{appt_id}/checkout")
def checkout(appt_id: int, body: CheckoutIn, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    appt = db.get(Appointment, appt_id)
    if not appt or appt.status != AppointmentStatus.confirmed:
        raise HTTPException(400, "Only confirmed appointments can be checked out")
    appt.revenue = body.revenue
    appt.status = AppointmentStatus.completed
    db.commit()
    return {"status": "completed", "revenue": body.revenue}


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(
    from_date: datetime = Query(...),
    to_date: datetime = Query(...),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    stats = svc.dashboard_stats(db, from_date, to_date)
    return DashboardOut(**stats)
