import json
import logging
import sys
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from prometheus_client import Counter, Histogram, generate_latest

from app.config import settings

BOOKINGS_SUBMITTED = Counter(
    "bookings_submitted_total", "Booking submissions", ["result"]
)
BOOKING_DURATION = Histogram(
    "booking_submit_duration_seconds", "Booking submit latency"
)

tracer = trace.get_tracer(settings.otel_service_name)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        span = trace.get_current_span()
        ctx = span.get_span_context()
        payload: dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if ctx.trace_id:
            payload["trace_id"] = format(ctx.trace_id, "032x")
        if ctx.span_id:
            payload["span_id"] = format(ctx.span_id, "016x")
        return json.dumps(payload)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.log_level)


_otel_ready = False


def setup_otel_app(app: Any) -> None:
    global _otel_ready
    if _otel_ready:
        return
    resource = Resource.create({"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)
    if settings.otel_exporter_otlp_endpoint:
        exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_otlp_endpoint, insecure=True
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
    else:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    _otel_ready = True


def setup_otel_engine(engine: Any) -> None:
    SQLAlchemyInstrumentor().instrument(engine=engine)


def metrics_response() -> bytes:
    return generate_latest()
