# Agent team

See [AGENTS.md](../AGENTS.md) for the table of roles. Loop rules: [loop-engineering.md](loop-engineering.md).

## Product / spec

- Create and groom GitHub issues from [PROJECT_HANDOFF.md §8](PROJECT_HANDOFF.md).
- Link PRs to issues; move labels (`status:backlog` → …).
- **Only role that may close** a feature issue, and **only** after a **`QA: PASS`** comment on that issue.
- On **`QA: FAIL`**: add a clear bug summary (expected vs actual), set `status:in-dev`, assign back to Full-stack; **keep open**.

## Full-stack

- Implement API, DB, customer and admin UI per issue acceptance criteria.
- Open PRs; set issue to `status:qa` when implementation is ready for verification.
- **Must not** run the official test sign-off (QA owns verification).
- **Must not** close issues.

## QA

- Run `make test`, manual flows, and steps listed in the issue.
- Comment exactly **`QA: PASS`** or **`QA: FAIL`** with command output or reproduction steps.
- **Must not** close or reopen issues.

## Platform

- Docker Compose, Render, CI/CD workflows, deploy docs.
- Same loop with Product closing after QA pass on platform issues.

## SRE / observability

- Booking journey telemetry, Prometheus alerts, responder agent.
- Same loop for observability-related issues.
