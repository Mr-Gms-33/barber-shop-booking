import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    declined = "declined"
    cancelled = "cancelled"
    completed = "completed"


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")


class Barber(Base):
    __tablename__ = "barbers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    schedules: Mapped[list["BarberSchedule"]] = relationship(back_populates="barber")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="barber")


class BarberSchedule(Base):
    __tablename__ = "barber_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    barber_id: Mapped[int] = mapped_column(ForeignKey("barbers.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon .. 6=Sun
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)

    barber: Mapped["Barber"] = relationship(back_populates="schedules")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    guest_name: Mapped[str] = mapped_column(String(120), nullable=False)
    guest_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    guest_email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    barber_id: Mapped[int | None] = mapped_column(ForeignKey("barbers.id"), nullable=True)
    any_barber: Mapped[bool] = mapped_column(Boolean, default=False)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.pending
    )
    revenue: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    service: Mapped["Service"] = relationship(back_populates="appointments")
    barber: Mapped["Barber | None"] = relationship(back_populates="appointments")
