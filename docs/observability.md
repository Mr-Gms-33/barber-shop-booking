# Observability

## Instrumented journey

**Customer booking submit:** `POST /api/bookings` — spans cover validation, slot hold, DB insert.

Signals:

- **Traces** — OpenTelemetry, exported via OTLP (Compose: collector → Tempo/Jaeger or console in dev).
- **Metrics** — `bookings_submitted_total`, `bookings_failed_total`, histogram `booking_submit_duration_seconds`.
- **Logs** — JSON structured logs with `trace_id` and `span_id` (no phone numbers or full guest PII in logs).

## Viewing locally

With `docker compose up`, open Grafana at http://localhost:3000 (default admin/admin). Dashboard: **Barber Booking**.

## User-impact alert

Prometheus rule `HighBookingFailureRate`: ratio of failed to total booking attempts over 5m exceeds threshold (see `observability/prometheus/alerts.yml`). This reflects customers unable to book — not CPU.

## Responder

See [responder/README.md](../responder/README.md). Webhook receives alert payload and runs remediation (e.g. log incident, optional Render redeploy hook).
