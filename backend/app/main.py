import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app import db
from app.db import Base
from app.routers import admin, public
from app.telemetry import metrics_response

logger = logging.getLogger(__name__)

app = FastAPI(title="Barber Booking API", version="1.0.0")

from app.telemetry import setup_logging, setup_otel_engine, setup_otel_app

setup_otel_app(app)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(public.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup() -> None:
    setup_logging()
    setup_otel_engine(db.engine)
    Base.metadata.create_all(bind=db.engine)
    _seed_if_empty()
    logger.info("API started")


def _seed_if_empty() -> None:
    from datetime import time

    from sqlalchemy import func, select

    from app.db import SessionLocal
    from app.models import Barber, BarberSchedule, Service

    db = SessionLocal()
    try:
        if db.scalar(select(func.count()).select_from(Service)) == 0:
            db.add_all(
                [
                    Service(name="Herrenhaarschnitt", duration_minutes=30, price=32.00),
                    Service(name="Bartpflege", duration_minutes=20, price=18.00),
                    Service(name="Haarschnitt & Bart", duration_minutes=45, price=42.00),
                    Service(name="Konturenschnitt", duration_minutes=15, price=22.00),
                    Service(name="Kinderhaarschnitt (bis 12)", duration_minutes=25, price=24.00),
                ]
            )
        if db.scalar(select(func.count()).select_from(Barber)) == 0:
            b1 = Barber(name="Marco Schneider")
            b2 = Barber(name="Ahmet Yilmaz")
            b3 = Barber(name="Jonas Weber")
            db.add_all([b1, b2, b3])
            db.flush()
            for barber_id in (b1.id, b2.id, b3.id):
                for dow in range(0, 5):
                    db.add(
                        BarberSchedule(
                            barber_id=barber_id,
                            day_of_week=dow,
                            start_time=time(9, 0),
                            end_time=time(17, 0),
                        )
                    )
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(content=metrics_response(), media_type="text/plain; version=0.0.4")
