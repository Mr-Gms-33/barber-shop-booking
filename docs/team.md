# Agent team

See [AGENTS.md](../AGENTS.md) for the table of roles.

**Full-stack agent** owns `backend/` and `frontend/`, schema migrations, and API contracts.

**QA agent** owns `backend/tests/`, frontend test config, and keeps `make test` green.

**Platform agent** owns `docker-compose.yml`, Dockerfiles, `.github/workflows/`, and `docs/deploy.md`.

**SRE agent** owns OpenTelemetry setup, Prometheus rules, Grafana dashboards, and `responder/`.

**Product agent** keeps the public issue tracker in sync with handoff §8 and records owner decisions.
