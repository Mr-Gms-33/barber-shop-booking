import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import FastAPI, Request

app = FastAPI(title="Barber Booking Responder")
INCIDENTS = Path(__file__).parent / "incidents"
INCIDENTS.mkdir(exist_ok=True)


@app.post("/alert")
async def on_alert(request: Request):
    payload = await request.json()
    alerts = payload.get("alerts") or [payload]
    names = [a.get("labels", {}).get("alertname", "unknown") for a in alerts]
    record = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "alertnames": names,
        "status": payload.get("status", "firing"),
        "action": "logged",
    }

    if os.getenv("AUTO_REMEDIATE") == "true" and "HighBookingFailureRate" in names:
        hook = os.getenv("RENDER_DEPLOY_HOOK_DEV")
        if hook:
            async with httpx.AsyncClient(timeout=30) as client:
                await client.post(hook)
            record["action"] = "triggered_render_redeploy_dev"

    out = INCIDENTS / "last.json"
    out.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record
