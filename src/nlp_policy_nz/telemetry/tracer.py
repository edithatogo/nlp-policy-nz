"""Tracing setup and small span helpers for pipeline instrumentation."""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path

SpanAttributeValue = bool | str | int | float | Sequence[bool | str | int | float] | None


@dataclass(frozen=True)
class TraceConfig:
    """Configuration for OpenTelemetry tracing exporters."""

    service_name: str = "nlp-policy-nz"
    enabled: bool = True
    console: bool = False
    trace_file: Path | None = None


@dataclass(frozen=True)
class TelemetryHandle:
    """Result returned by tracing configuration."""

    config: TraceConfig
    available: bool
    exporters: tuple[str, ...]


_CONFIGURED_HANDLE: TelemetryHandle | None = None


def _env_flag(name: str, default: bool) -> bool:
    """Read a boolean environment flag."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _span_to_dict(span: object) -> dict[str, object]:
    """Convert an OpenTelemetry readable span into JSON-serialisable data."""
    get_span_context = span.get_span_context
    context = get_span_context()
    parent = getattr(span, "parent", None)
    parent_span_id = getattr(parent, "span_id", None) if parent is not None else None
    return {
        "name": span.name,
        "context": {
            "trace_id": f"{context.trace_id:032x}",
            "span_id": f"{context.span_id:016x}",
            "parent_span_id": f"{parent_span_id:016x}" if parent_span_id else None,
        },
        "kind": str(getattr(span, "kind", "")),
        "start_time_unix_ns": getattr(span, "start_time", None),
        "end_time_unix_ns": getattr(span, "end_time", None),
        "attributes": dict(getattr(span, "attributes", {}) or {}),
        "events": [
            {
                "name": event.name,
                "timestamp_unix_ns": event.timestamp,
                "attributes": dict(event.attributes or {}),
            }
            for event in getattr(span, "events", []) or []
        ],
        "status": {
            "status_code": str(getattr(getattr(span, "status", None), "status_code", "")),
            "description": getattr(getattr(span, "status", None), "description", None),
        },
    }


def _make_file_exporter(trace_file: Path) -> object:
    """Create a JSONL span exporter without requiring SDK imports at module load."""
    from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

    class JsonLinesSpanExporter(SpanExporter):
        """Write each exported span as one JSON object per line."""

        def __init__(self, output_path: Path) -> None:
            self.output_path = output_path
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

        def export(self, spans: Sequence[object]) -> object:
            with self.output_path.open("a", encoding="utf-8") as handle:
                for span in spans:
                    handle.write(json.dumps(_span_to_dict(span), sort_keys=True))
                    handle.write("\n")
            return SpanExportResult.SUCCESS

        def shutdown(self) -> None:
            return None

    return JsonLinesSpanExporter(trace_file)


def configure_tracing(
    *,
    service_name: str = "nlp-policy-nz",
    enabled: bool | None = None,
    console: bool | None = None,
    trace_file: str | Path | None = None,
) -> TelemetryHandle:
    """Configure OpenTelemetry tracing for pipeline runs.

    The function is intentionally safe to call in environments where the
    OpenTelemetry SDK has not yet been installed; it returns a no-op handle
    instead of breaking imports or CLI startup.
    """
    global _CONFIGURED_HANDLE

    effective_enabled = _env_flag("NLP_POLICY_NZ_TRACE", True) if enabled is None else enabled
    effective_console = (
        _env_flag("NLP_POLICY_NZ_TRACE_CONSOLE", False) if console is None else console
    )
    trace_path = Path(trace_file).resolve() if trace_file is not None else None
    config = TraceConfig(
        service_name=service_name,
        enabled=effective_enabled,
        console=effective_console,
        trace_file=trace_path,
    )

    if not effective_enabled:
        return TelemetryHandle(config=config, available=False, exporters=())

    if _CONFIGURED_HANDLE is not None:
        return _CONFIGURED_HANDLE

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    except Exception:
        return TelemetryHandle(config=config, available=False, exporters=())

    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
    exporters: list[str] = []
    if effective_console:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        exporters.append("console")
    if trace_path is not None:
        provider.add_span_processor(BatchSpanProcessor(_make_file_exporter(trace_path)))
        exporters.append("jsonl-file")
    trace.set_tracer_provider(provider)

    handle = TelemetryHandle(config=config, available=True, exporters=tuple(exporters))
    _CONFIGURED_HANDLE = handle
    return handle


@contextmanager
def pipeline_span(
    name: str,
    attributes: Mapping[str, SpanAttributeValue] | None = None,
) -> Iterator[object]:
    """Start a named pipeline span when OpenTelemetry is available."""
    try:
        from opentelemetry import trace
    except Exception:
        with nullcontext() as span:
            yield span
        return

    tracer = trace.get_tracer("nlp_policy_nz.pipeline")
    start = time.perf_counter()
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        try:
            yield span
        finally:
            span.set_attribute("duration_ms", (time.perf_counter() - start) * 1000)


def set_span_attribute(key: str, value: SpanAttributeValue) -> None:
    """Set an attribute on the current active span when tracing is active."""
    try:
        from opentelemetry import trace
    except Exception:
        return
    span = trace.get_current_span()
    if span is not None:
        span.set_attribute(key, value)


def record_span_exception(exc: BaseException) -> None:
    """Record an exception on the current active span when tracing is active."""
    try:
        from opentelemetry import trace
    except Exception:
        return
    span = trace.get_current_span()
    if span is not None:
        span.record_exception(exc)
