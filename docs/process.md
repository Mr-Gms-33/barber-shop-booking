# Development process

1. **Spec first** — Changes to behavior require an update to `PROJECT_HANDOFF.md` or a tracked issue with acceptance criteria.
2. **Task tracker** — [GitHub Issues](https://github.com/Mr-Gms-33/barber-shop-booking/issues); one testable criterion per issue (§8). See [loop-engineering.md](loop-engineering.md).
3. **Loop** — Product grooms → Full-stack implements (does **not** close; does **not** own QA sign-off) → QA **`QA: PASS`** / **`QA: FAIL`** (does **not** close) → Product **closes on PASS** or documents bug and sends back to Full-stack on FAIL.
4. **Branches** — `main` (production-ready), feature branches, PRs reference issue numbers.
5. **CI** — Every PR runs backend and frontend tests (QA uses the same commands for evidence).
6. **CD** — Merge to `main` deploys **dev** on Render; **production** via manual workflow (see `deploy.md`).
7. **Definition of done** — Issue closed by **Product** after **QA: PASS**; code merged; acceptance criterion verified.
