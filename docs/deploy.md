# Deployment (Render)

## Environments

| Env | Trigger | Purpose |
|-----|---------|---------|
| **dev** | Push to `main` (GitHub Actions) | Integration testing on public URL |
| **prod** | Manual `workflow_dispatch` | Live demo / production |

## Render services

1. **PostgreSQL** — managed database; copy `DATABASE_URL` to web services.
2. **Web service (API)** — Docker context `backend/`, port 8000, health check `/health`.
3. **Static site or web service (UI)** — build `frontend/` with `VITE_API_URL` pointing to API.

Set secrets in Render and GitHub:

- `DATABASE_URL`, `ADMIN_PASSWORD`, `JWT_SECRET`, `BOOKING_CUTOFF_HOURS=2`
- `OTEL_EXPORTER_OTLP_ENDPOINT` (optional; Grafana Cloud or self-hosted)

## CI/CD (GitHub Actions)

- **ci.yml** — on PR: test backend + frontend.
- **cd-dev.yml** — on push to `main`: deploy dev (Render deploy hook or API).
- **cd-prod.yml** — manual: deploy production + tag; document previous image/tag for rollback.

## Rollback

1. In Render, redeploy previous **successful** deploy for API and UI.
2. Or re-run `cd-prod.yml` with input `git_ref` set to last known-good commit.
3. DB migrations: prefer forward-only fixes; keep migration backups before prod deploy.

Replace placeholder deploy hooks in workflows after creating Render services.
