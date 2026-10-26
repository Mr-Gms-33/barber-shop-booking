# Deployment (Render)

## Public URLs (after Blueprint apply)

| Service | URL |
|---------|-----|
| **Customer UI** | https://barber-booking-web.onrender.com |
| **API** | https://barber-booking-api.onrender.com |
| **API docs** | https://barber-booking-api.onrender.com/docs |

Update `README.md` with these once live. Free tier may take ~1 min to wake on first visit.

## One-time setup (you do this in the browser)

1. Sign in at [render.com](https://render.com) and connect GitHub account **Mr-Gms-33**.
2. **New → Blueprint** → select repo **barber-shop-booking** → apply [render.yaml](../render.yaml).  
   If validation fails on `plan` for the static site, pull latest `main` (static UI must not set `plan: free`).
3. When prompted, set **`ADMIN_PASSWORD`** (e.g. `changeme` for demo, or a strong password).
4. Wait until **barber-booking-api** and **barber-booking-web** are **Live** (database migrates on first API start).

If a sync **failed** partway: open **Project_01 → Syncs → Manual sync** (or Blueprint → Sync) after pulling latest `main`. Ensure **`ADMIN_PASSWORD`** is set under **barber-booking-api → Environment**. Delete broken duplicate services only if Render shows stuck failed creates.
5. Open the UI URL, book a test appointment; admin login: **`admin`** + your `ADMIN_PASSWORD`.

## GitHub Actions CD (optional, for rubric)

In each Render service → **Settings → Deploy Hook**, copy URL:

| GitHub secret | Render service |
|---------------|----------------|
| `RENDER_DEPLOY_HOOK_API` | barber-booking-api |
| `RENDER_DEPLOY_HOOK_WEB` | barber-booking-web |

Optional separate prod hooks:

- `RENDER_DEPLOY_HOOK_API_PROD` / `RENDER_DEPLOY_HOOK_WEB_PROD`  
  (same URLs if you only have one environment on free tier)

- **cd-dev.yml** — runs on push to `main`, POSTs hooks.  
- **cd-prod.yml** — manual **Run workflow** (production / rollback by `git_ref`).

## Environments

| Env | Trigger | Purpose |
|-----|---------|---------|
| **dev** | Push to `main` + deploy hooks | Auto redeploy |
| **prod** | Manual `cd-prod.yml` | Same services on free tier; use for “promote/rollback” ritual |

## Rollback

1. Render dashboard → service → **Deploys** → **Redeploy** previous successful deploy.  
2. Or run **CD Production** workflow with `git_ref` = last good commit SHA.

## Local vs Render

- Local: `docker compose up` or `scripts/run-local.ps1`  
- Render: managed Postgres + Docker API + static React build (`VITE_API_URL` set in `render.yaml`)
