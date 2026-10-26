# Barber Shop Online Booking

Small single-shop barber booking: customers reserve services online; staff approve, assign barbers, check out visits, and view sales.

**Course submission:** [docs/SUBMISSION.md](docs/SUBMISSION.md) · **Repo:** https://github.com/Mr-Gms-33/barber-shop-booking

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

**Issues (§8 acceptance criteria):** https://github.com/Mr-Gms-33/barber-shop-booking/issues — 26 tasks with QA/Product loop ([docs/loop-engineering.md](docs/loop-engineering.md)).

## Agent team

See [AGENTS.md](AGENTS.md) and [docs/process.md](docs/process.md).

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL  
- **Frontend:** React (Vite, TypeScript)  
- **Deploy:** Render — [docs/deploy.md](docs/deploy.md) + [render.yaml](render.yaml)

### Live demo (Render)

| | URL |
|---|-----|
| **App** | https://barber-booking-web.onrender.com |
| **API docs** | https://barber-booking-api.onrender.com/docs |
| **Health** | https://barber-booking-api.onrender.com/health |

**Production admin:** `admin` / `changeme` — wake API via **Health** link first on free tier (~1 min).

## Run locally

**With Docker** (full stack: Postgres, observability):

```bash
docker compose up --build
```

**Without Docker** (Windows — API + UI only):

```powershell
.\scripts\run-local.ps1
```

- Customer UI: http://localhost:5173  
- API docs: http://localhost:8000/docs  
- **Admin login (local dev):** username `admin`, password `changeme` — change via `ADMIN_PASSWORD` in production.
- **Demo catalog (Germany, EUR):** barbers Marco Schneider, Ahmet Yilmaz, Jonas Weber; services such as Herrenhaarschnitt (32 €), Bartpflege (18 €). Seeded on first API start when the database is empty. If you already ran the API once, delete `backend/local.db` (or reset Postgres) and restart to reload seed data.

If `/docs` shows **connection refused**, nothing is listening on port 8000 — start the backend (script above or `uvicorn` in `backend/`).

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
