# On-call responder agent

When Prometheus fires **HighBookingFailureRate**, Alertmanager (or Grafana OnCall) should POST to the responder webhook.

## Run locally

```bash
pip install -r requirements.txt
uvicorn agent:app --host 0.0.0.0 --port 9000
```

Configure webhook URL: `http://responder:9000/alert`

## Behavior

1. Parse alert payload (Alertmanager format).
2. Log incident with trace-friendly JSON (no PII).
3. Optional: call `RENDER_DEPLOY_HOOK_DEV` to restart dev API if `AUTO_REMEDIATE=true`.
4. Write `incidents/last.json` for audit.

This satisfies the course **responder agent** criterion when wired to your alert route.
