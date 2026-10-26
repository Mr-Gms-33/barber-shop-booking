# Barber Shop Online Booking

Small single-shop barber booking: customers reserve services online; staff approve, assign barbers, check out visits, and view sales.

## Problem

Phone bookings waste time and cause double-booking. Customers need to pick a **service**, **time**, and optional **barber** without calling. Staff need one place to **approve** requests, **assign** barbers when needed, **check out** after the visit, and see **history** and **revenue**.

## Behavior (v1)

- Guest booking (name + phone; email optional). No online payment — pay at shop.
- New bookings are **`pending`** until admin accepts or rejects.
- Customer status page via **booking code** (no email/SMS in v1).
- Cancel/reschedule allowed only **more than 2 hours** before start; reschedule returns to **`pending`**.
- **`pending`** and **`confirmed`** appointments block barber slots.
- One service per appointment. Invalid slot/barber shows **suggestions** (alternate times/barbers).
- Admin: catalog, barbers, weekly hours, pending queue, checkout (adjustable revenue), history, sales dashboard.

Full product spec: [docs/PROJECT_HANDOFF.md](docs/PROJECT_HANDOFF.md).

## Task tracker

Create GitHub Issues from [docs/PROJECT_HANDOFF.md §8](docs/PROJECT_HANDOFF.md) (acceptance criteria). Link your repo Issues page here after push:

`https://github.com/<owner>/<repo>/issues`

## Agent team

See [AGENTS.md](AGENTS.md) and [docs/process.md](docs/process.md).

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL  
- **Frontend:** React (Vite, TypeScript)  
- **Deploy:** Render (see [docs/deploy.md](docs/deploy.md))

## Run locally (one command)

```bash
docker compose up --build
```

- Customer UI: http://localhost:5173  
- API docs: http://localhost:8000/docs  
- Default admin (dev only): `admin` / `changeme` — set `ADMIN_PASSWORD` in production.

Run tests:

```bash
docker compose run --rm backend pytest
docker compose run --rm frontend npm test -- --run
```

Or from host (requires local Postgres matching `.env.example`):

```bash
make test
```

## Observability & alerts

Booking journey is instrumented with OpenTelemetry (traces, metrics, structured logs sharing trace ID). Grafana/Prometheus in Compose — see [docs/observability.md](docs/observability.md).

User-impact alert: elevated **booking submission failures** (not CPU). Responder: [responder/README.md](responder/README.md).

## License

Course project — Mounir.
