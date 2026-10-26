# Agent context — Barber Shop Booking

## Project summary

Single-barber-shop online booking (guest customers, admin staff). Spec: [docs/PROJECT_HANDOFF.md](docs/PROJECT_HANDOFF.md).

## Agent team & process

| Role | Responsibility |
|------|----------------|
| Product / spec | Tracker aligned with handoff §8; owner decisions on open product points |
| Full-stack | API, DB, customer + admin UI |
| QA | Unit (domain rules), integration (API+DB), frontend critical paths |
| Platform | Docker Compose, Render deploy, CI/CD |
| SRE / observability | Booking journey telemetry, user-impact alerts, responder agent |

How we work: [docs/process.md](docs/process.md). **Loop engineering:** [docs/loop-engineering.md](docs/loop-engineering.md). Role details: [docs/team.md](docs/team.md).

**Tracker:** https://github.com/Mr-Gms-33/barber-shop-booking/issues — Product creates/grooms; Full-stack implements (no test sign-off); QA comments `QA: PASS` / `QA: FAIL` only; Product closes on PASS or returns bugs to Full-stack.

## Modular docs

- [docs/PROJECT_HANDOFF.md](docs/PROJECT_HANDOFF.md) — product, journeys, acceptance criteria  
- [docs/process.md](docs/process.md) — workflow, branches, definition of done  
- [docs/team.md](docs/team.md) — agent responsibilities  
- [docs/deploy.md](docs/deploy.md) — Render, environments, rollback  
- [docs/observability.md](docs/observability.md) — traces, metrics, alerts  

## Domain rules (implementers)

```
pending --accept--> confirmed --checkout--> completed
pending --reject--> declined
pending|confirmed --cancel (customer if >2h)--> cancelled
confirmed --reschedule--> pending

Cutoff: BOOKING_CUTOFF_HOURS=2 (env)
Pending + confirmed block barber slots.
```

## Commands

- `docker compose up --build` — full stack  
- `make test` — backend + frontend tests  
- `make migrate` — apply Alembic migrations  

## Defaults (unless owner overrides)

- Guest: name + phone required; email optional; status via booking code + last 4 phone digits  
- One service per appointment; reschedule → `pending`
