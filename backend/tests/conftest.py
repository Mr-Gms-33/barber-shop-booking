import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "")

from datetime import datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Appointment, Barber, BarberSchedule, Service


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    import app.db as app_db

    app_db.engine = eng
    app_db.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)


@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Appointment).delete()
    session.query(BarberSchedule).delete()
    session.query(Barber).delete()
    session.query(Service).delete()
    session.commit()

    svc = Service(name="Cut", duration_minutes=30, price=20, active=True)
    barber = Barber(name="Joe", active=True)
    session.add_all([svc, barber])
    session.commit()
    for dow in range(0, 5):
        session.add(
            BarberSchedule(
                barber_id=barber.id,
                day_of_week=dow,
                start_time=time(9, 0),
                end_time=time(17, 0),
            )
        )
    session.commit()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def next_weekday_10am():
    d = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    if d < datetime.utcnow():
        d += timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d
