# Project submission (Final Project — Abgabe)

**Author:** Mounir  
**Repository:** https://github.com/Mr-Gms-33/barber-shop-booking  
**Spec:** [PROJECT_HANDOFF.md](PROJECT_HANDOFF.md)

## What to submit on the course platform

| Item | Link / value |
|------|----------------|
| **Git repo** | https://github.com/Mr-Gms-33/barber-shop-booking |
| **Public app** | https://barber-booking-web.onrender.com |
| **API (Swagger)** | https://barber-booking-api.onrender.com/docs |
| **Task tracker** | https://github.com/Mr-Gms-33/barber-shop-booking/issues (26 issues, QA history in comments) |
| **Documentation** | [README.md](../README.md), [AGENTS.md](../AGENTS.md) |

**Admin demo login (Render):** `admin` / `changeme` (unless you changed `ADMIN_PASSWORD` in Render).

**Free tier note:** Open https://barber-booking-api.onrender.com/health first and wait ~60s so the API wakes up before reviewers test booking or admin login.

## Peer review (required to pass)

You must **review 3 other participants’ projects** on the course platform. Submitting without peer reviews does **not** pass.

## 60-second demo script (for you or reviewers)

1. Open the **Book** page → choose **Herrenhaurschnitt** → date/time → barber → name + phone → submit → note **booking code**.
2. **Admin** → login → **Pending** → Accept → **Checkout** with EUR amount.
3. **My booking** → code + last 4 phone digits → see status **confirmed** / **completed**.
4. (Optional) `make test` or GitHub **Actions → CI** green on `main`.

## Rubric self-check (12 criteria, 24 pts max, 10 to pass)

| Criterion | Where to look | Est. |
|-----------|----------------|------|
| Problem description | README § Problem | 2 |
| Product spec + tracker | PROJECT_HANDOFF.md + GitHub Issues | 2 |
| Agent team | AGENTS.md, loop-engineering.md | 2 |
| Context / modular docs | AGENTS.md → docs/* | 2 |
| Full-stack app | Live URLs or `docker compose up` / run-local.ps1 | 2 |
| Tests | CI workflow; `backend` pytest + `frontend` vitest | 2 |
| Containerization | docker-compose.yml | 2 |
| Deployment | Render URLs above | 1–2 |
| CI/CD | `.github/workflows/ci.yml` (+ cd-dev/cd-prod hooks if configured) | 1–3 |
| Observability | docs/observability.md, OTel + `/metrics`, Compose Grafana | 1–2 |
| User-impact alert | observability/prometheus/alerts.yml | 1–2 |
| Responder agent | responder/agent.py, responder/README.md | 1–2 |

## Before you click “Submit”

- [ ] GitHub `main` is up to date; CI last run **green**
- [ ] Render: **barber-booking-api**, **barber-booking-web**, **barber-booking-db** show Deployed / Available
- [ ] `/health` returns `{"status":"ok"}` after wake-up
- [ ] One test booking works end-to-end
- [ ] **3 peer reviews** scheduled or done on the platform
- [ ] README lists live URLs and admin login

## Local backup (if Render is slow during review)

```powershell
.\scripts\run-local.ps1
```

Then http://localhost:5173 and http://localhost:8000/docs — same behavior, SQLite instead of Render Postgres.

---

## Abgabe-Checkliste (Deutsch)

1. **Repo-Link** auf der Kursplattform einreichen.  
2. **Live-URL** der App eintragen (Render).  
3. **README & AGENTS.md** sind auf Englisch (Kursvorgabe).  
4. **Peer Review:** 3 fremde Projekte bewerten.  
5. **API aufwecken:** vor Demo `/health` aufrufen (Free Tier).  
6. **Login Admin:** `admin` / `changeme`.
