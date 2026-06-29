"""Tests for Track 19 OpenTelemetry helpers and pipeline instrumentation."""

from __future__ import annotations

import builtins
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from nlp_policy_nz.telemetry import tracer as tracer_module
from nlp_policy_nz.telemetry.tracer import _make_file_exporter, _span_to_dict, configure_tracing

if TYPE_CHECKING:
    from collections.abc import Iterator


class _FakeContext:
    trace_id = 1
    span_id = 2


class _FakeParent:
    span_id = 3


class _FakeEvent:
    def __init__(self) -> None:
        self.name = "event"
        self.timestamp = 4
        self.attributes = {"key": "value"}


class _FakeStatus:
    status_code = "OK"
    description = None


class _FakeReadableSpan:
    def __init__(self) -> None:
        self.name = "pipeline.test"
        self.parent = _FakeParent()
        self.kind = "INTERNAL"
        self.start_time = 5
        self.end_time = 6
        self.attributes = {"pipeline.record_count": 2}
        self.events = [_FakeEvent()]
        self.status = _FakeStatus()

    def get_span_context(self) -> _FakeContext:
        return _FakeContext()


class _ActiveSpan:
    def __init__(self) -> None:
        self.attributes: dict[str, Any] = {}
        self.exceptions: list[BaseException] = []

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def record_exception(self, exc: BaseException) -> None:
        self.exceptions.append(exc)


def test_configure_tracing_can_disable_exporters() -> None:
    """Tracing can be disabled for lightweight local and CI probes."""
    handle = configure_tracing(enabled=False)

    assert handle.available is False
    assert handle.exporters == ()
    assert handle.config.enabled is False


def test_tracing_falls_back_when_sdk_import_fails(monkeypatch) -> None:
    """Telemetry helpers degrade to no-op behavior when OTel is unavailable."""
    original_import = builtins.__import__

    def blocked_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name.startswith("opentelemetry"):
            raise ImportError(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    monkeypatch.setenv("NLP_POLICY_NZ_TRACE", "yes")
    monkeypatch.setenv("NLP_POLICY_NZ_TRACE_CONSOLE", "yes")
    monkeypatch.setattr(tracer_module, "_CONFIGURED_HANDLE", None)

    handle = configure_tracing(enabled=None, console=None)
    with tracer_module.pipeline_span("pipeline.noop") as span:
        tracer_module.set_span_attribute("key", "value")
        tracer_module.record_span_exception(RuntimeError("boom"))

    assert handle.available is False
    assert handle.config.console is True
    assert span is None


def test_configure_tracing_reuses_existing_handle(monkeypatch) -> None:
    """Repeated setup calls return the already configured handle."""
    existing = tracer_module.TelemetryHandle(
        config=tracer_module.TraceConfig(service_name="existing"),
        available=True,
        exporters=("console",),
    )
    monkeypatch.setattr(tracer_module, "_CONFIGURED_HANDLE", existing)

    assert configure_tracing(service_name="ignored") is existing


def test_span_to_dict_serializes_core_trace_fields() -> None:
    """JSONL exporter payloads include IDs, attributes, events, and status."""

    class Context:
        trace_id = 1
        span_id = 2

    class Parent:
        span_id = 3

    class Event:
        def __init__(self) -> None:
            self.name = "event"
            self.timestamp = 4
            self.attributes = {"key": "value"}

    class Status:
        status_code = "OK"
        description = None

    class Span:
        def __init__(self) -> None:
            self.name = "pipeline.test"
            self.parent = Parent()
            self.kind = "INTERNAL"
            self.start_time = 5
            self.end_time = 6
            self.attributes = {"pipeline.record_count": 2}
            self.events = [Event()]
            self.status = Status()

        def get_span_context(self) -> Context:
            return Context()

    payload = _span_to_dict(Span())

    assert payload["name"] == "pipeline.test"
    assert payload["context"]["trace_id"] == "00000000000000000000000000000001"
    assert payload["context"]["span_id"] == "0000000000000002"
    assert payload["context"]["parent_span_id"] == "0000000000000003"
    assert payload["attributes"]["pipeline.record_count"] == 2
    assert payload["events"][0]["attributes"] == {"key": "value"}


def test_configure_tracing_registers_console_and_file_exporters(monkeypatch) -> None:
    """SDK-backed setup registers span processors and exporter names."""
    providers: list[Any] = []

    class Resource:
        @staticmethod
        def create(values: dict[str, str]) -> dict[str, str]:
            return values

    class Provider:
        def __init__(self, resource: dict[str, str]) -> None:
            self.resource = resource
            self.processors: list[Any] = []

        def add_span_processor(self, processor: Any) -> None:
            self.processors.append(processor)

    class BatchSpanProcessor:
        def __init__(self, exporter: Any) -> None:
            self.exporter = exporter

    class ConsoleSpanExporter:
        pass

    class SpanExporter:
        pass

    class SpanExportResult:
        SUCCESS = "success"

    trace_module = ModuleType("opentelemetry.trace")

    def set_tracer_provider(provider: Provider) -> None:
        providers.append(provider)

    trace_module.set_tracer_provider = set_tracer_provider  # type: ignore[attr-defined]
    otel_module = ModuleType("opentelemetry")
    otel_module.trace = trace_module  # type: ignore[attr-defined]
    resources_module = ModuleType("opentelemetry.sdk.resources")
    resources_module.SERVICE_NAME = "service.name"  # type: ignore[attr-defined]
    resources_module.Resource = Resource  # type: ignore[attr-defined]
    sdk_trace_module = ModuleType("opentelemetry.sdk.trace")
    sdk_trace_module.TracerProvider = Provider  # type: ignore[attr-defined]
    export_module = ModuleType("opentelemetry.sdk.trace.export")
    export_module.BatchSpanProcessor = BatchSpanProcessor  # type: ignore[attr-defined]
    export_module.ConsoleSpanExporter = ConsoleSpanExporter  # type: ignore[attr-defined]
    export_module.SpanExporter = SpanExporter  # type: ignore[attr-defined]
    export_module.SpanExportResult = SpanExportResult  # type: ignore[attr-defined]

    for name, module in {
        "opentelemetry": otel_module,
        "opentelemetry.trace": trace_module,
        "opentelemetry.sdk.resources": resources_module,
        "opentelemetry.sdk.trace": sdk_trace_module,
        "opentelemetry.sdk.trace.export": export_module,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setattr(tracer_module, "_CONFIGURED_HANDLE", None)

    handle = configure_tracing(
        service_name="svc",
        console=True,
        trace_file=Path(".tmp") / "telemetry-tests" / "trace.jsonl",
    )

    assert handle.available is True
    assert handle.exporters == ("console", "jsonl-file")
    assert providers[0].resource == {"service.name": "svc"}
    assert len(providers[0].processors) == 2


def test_jsonl_file_exporter_writes_span_payload(monkeypatch) -> None:
    """File exporter writes one JSON span payload per line."""

    class SpanExporter:
        pass

    class SpanExportResult:
        SUCCESS = "success"

    export_module = ModuleType("opentelemetry.sdk.trace.export")
    export_module.SpanExporter = SpanExporter  # type: ignore[attr-defined]
    export_module.SpanExportResult = SpanExportResult  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "opentelemetry.sdk.trace.export", export_module)

    output = Path(".tmp") / "telemetry-tests" / f"exporter-{uuid4().hex}.jsonl"
    exporter = _make_file_exporter(output)
    result = exporter.export([_FakeReadableSpan()])  # type: ignore[attr-defined]
    exporter.shutdown()  # type: ignore[attr-defined]

    assert result == "success"
    payload = json.loads(output.read_text(encoding="utf-8").strip())
    assert payload["name"] == "pipeline.test"


def test_span_helpers_use_current_span(monkeypatch) -> None:
    """Span context helper sets attributes and records exceptions."""
    active = _ActiveSpan()

    class Tracer:
        @contextmanager
        def start_as_current_span(self, _name: str) -> Iterator[_ActiveSpan]:
            yield active

    trace_module = ModuleType("opentelemetry.trace")
    trace_module.get_tracer = lambda _name: Tracer()  # type: ignore[attr-defined]
    trace_module.get_current_span = lambda: active  # type: ignore[attr-defined]
    otel_module = ModuleType("opentelemetry")
    otel_module.trace = trace_module  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "opentelemetry", otel_module)
    monkeypatch.setitem(sys.modules, "opentelemetry.trace", trace_module)

    with tracer_module.pipeline_span("pipeline.test", {"initial": "value"}):
        tracer_module.set_span_attribute("later", 2)
        tracer_module.record_span_exception(ValueError("bad"))

    assert active.attributes["initial"] == "value"
    assert active.attributes["later"] == 2
    assert "duration_ms" in active.attributes
    assert len(active.exceptions) == 1


def test_process_legislation_emits_pipeline_spans(monkeypatch) -> None:
    """Legislation processing configures trace sidecars and names major spans."""
    from nlp_policy_nz import pipeline_api

    tmp_path = Path(".tmp") / "telemetry-tests" / "process-legislation"
    tmp_path.mkdir(parents=True, exist_ok=True)
    input_file = tmp_path / "act.txt"
    output_file = tmp_path / "legislation.parquet"
    input_file.write_text("The Minister must report.", encoding="utf-8")

    configured: dict[str, Any] = {}
    spans: list[tuple[str, dict[str, Any]]] = []
    attributes: dict[str, Any] = {}

    @contextmanager
    def fake_span(name: str, attrs: dict[str, Any] | None = None) -> Iterator[None]:
        spans.append((name, attrs or {}))
        yield

    class FakeNlp:
        def __init__(self) -> None:
            self.pipe_names: list[str] = []

        def add_pipe(self, *_args: Any, **_kwargs: Any) -> None:
            self.pipe_names.append("deontic_modality")

        def __call__(self, _text: str) -> Any:
            return type("Doc", (), {"ents": [], "spans": {}})()

    def fake_serialize(_records: list[Any], out: str | Path) -> Path:
        path = Path(out)
        path.write_bytes(b"parquet")
        return path

    monkeypatch.setattr(pipeline_api, "configure_tracing", lambda **kwargs: configured.update(kwargs))
    monkeypatch.setattr(pipeline_api, "pipeline_span", fake_span)
    monkeypatch.setattr(pipeline_api, "set_span_attribute", lambda key, value: attributes.update({key: value}))
    monkeypatch.setattr(pipeline_api, "create_nlp_pipeline", FakeNlp)
    monkeypatch.setattr(pipeline_api, "create_citation_ruler", lambda _nlp: None)
    monkeypatch.setattr(
        pipeline_api,
        "chunk_legislation_document",
        lambda _text, _nlp, year, number: [{"doc_id": "doc-1", "text": "Body"}],
    )
    monkeypatch.setattr(pipeline_api, "_extract_te_reo_terms", lambda _text: [])
    monkeypatch.setattr(pipeline_api, "_extract_citations", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "detect_modality", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "detect_temporal_expressions", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "classify_legal_effect", lambda _text, _nlp: None)
    monkeypatch.setattr(pipeline_api, "serialize_to_parquet", fake_serialize)

    result = pipeline_api.process_legislation(input_file, output_file, generate_embeddings=False)

    span_names = [name for name, _attrs in spans]
    assert result == output_file.resolve()
    assert configured["trace_file"] == output_file.resolve().with_suffix(".traces.jsonl")
    assert "pipeline.process_legislation" in span_names
    assert "pipeline.legislation.file" in span_names
    assert "pipeline.legislation.chunk" in span_names
    assert "pipeline.storage.serialize" in span_names
    assert attributes["pipeline.input_file_count"] == 1
