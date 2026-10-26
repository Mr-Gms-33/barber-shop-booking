# Development process

1. **Spec first** — Changes to behavior require an update to `PROJECT_HANDOFF.md` or a tracked issue with acceptance criteria.
2. **Task tracker** — GitHub Issues; link PRs to issues; close when §8 criteria met.
3. **Branches** — `main` (production-ready), feature branches, PRs to `main`.
4. **CI** — Every PR runs backend unit/integration tests and frontend tests.
5. **CD** — Merge to `main` deploys **dev** on Render; **production** via manual workflow (see `deploy.md`).
6. **Definition of done** — Feature works E2E locally in Compose, tests added/updated, observability on user-facing paths where relevant.
