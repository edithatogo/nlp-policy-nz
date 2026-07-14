"""Tests for the Track 62 vLLM local inference runtime evaluation helpers."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from nlp_policy_nz.semantic import vllm_runtime as module


@dataclass(frozen=True)
class _FakeSamplingParams:
    max_tokens: int
    temperature: float
    top_p: float


@dataclass(frozen=True)
class _FakeGeneratedText:
    text: str


@dataclass(frozen=True)
class _FakeGenerationOutput:
    prompt: str
    outputs: list[_FakeGeneratedText]


class _FakeVLLMEngine:
    def __init__(self, model: str, **kwargs: object) -> None:
        self.model = model
        self.kwargs = kwargs
        self.prompts: list[list[str]] = []
        self.sampling_params: list[_FakeSamplingParams] = []

    def generate(self, prompts: list[str], sampling_params: _FakeSamplingParams) -> list[_FakeGenerationOutput]:
        self.prompts.append(prompts)
        self.sampling_params.append(sampling_params)
        return [_FakeGenerationOutput(prompt=prompts[0], outputs=[_FakeGeneratedText(text="offline answer")])]


class _OpenAICompatibleHandler(BaseHTTPRequestHandler):
    body: dict[str, Any] | None = None

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
        type(self).body = payload
        response = {
            "id": "cmpl-track62",
            "object": "text_completion",
            "choices": [{"index": 0, "text": "endpoint answer"}],
        }
        blob = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(blob)))
        self.end_headers()
        self.wfile.write(blob)

    def log_message(self, message: str, *args: object) -> None:  # noqa: A003 - stdlib handler API
        return


@pytest.fixture
def openai_compatible_server() -> tuple[str, type[_OpenAICompatibleHandler]]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _OpenAICompatibleHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        yield base_url, _OpenAICompatibleHandler
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_vllm_endpoint_generation_uses_openai_compatible_fixture(
    openai_compatible_server: tuple[str, type[_OpenAICompatibleHandler]],
) -> None:
    base_url, handler = openai_compatible_server

    result = module.generate_completion_via_openai_endpoint(
        "Summarise the clause.",
        endpoint_url=base_url,
        model_name="demo-model",
        max_tokens=16,
        temperature=0.0,
        top_p=1.0,
    )

    assert result.generated_text == "endpoint answer"
    assert result.mode == "endpoint"
    assert result.model_name == "demo-model"
    assert handler.body is not None
    assert handler.body["prompt"] == "Summarise the clause."
    assert handler.body["model"] == "demo-model"
    assert handler.body["max_tokens"] == 16


def test_vllm_offline_generation_uses_engine_and_sampling_params(monkeypatch) -> None:
    engine = _FakeVLLMEngine("demo-model")

    def fake_engine_factory(model_name: str, **kwargs: object) -> _FakeVLLMEngine:
        assert model_name == "demo-model"
        return engine

    monkeypatch.setattr(module, "_create_vllm_engine", fake_engine_factory)
    monkeypatch.setattr(module, "_create_sampling_params", _FakeSamplingParams)

    result = module.generate_completion_via_vllm(
        "Analyse the clause.",
        model_name="demo-model",
        max_tokens=24,
        temperature=0.2,
        top_p=0.91,
    )

    assert result.generated_text == "offline answer"
    assert result.mode == "offline"
    assert engine.prompts == [["Analyse the clause."]]
    assert engine.sampling_params[0] == _FakeSamplingParams(
        max_tokens=24,
        temperature=0.2,
        top_p=0.91,
    )


def test_vllm_offline_generation_reports_missing_dependency(monkeypatch) -> None:
    def fake_engine_factory(*args: object, **kwargs: object) -> object:
        raise ImportError("vllm unavailable")

    monkeypatch.setattr(module, "_create_vllm_engine", fake_engine_factory)

    with pytest.raises(ImportError, match="optional 'vllm' extra"):
        module.generate_completion_via_vllm("Prompt", model_name="demo-model")


def test_track62_evidence_report_records_optional_deployment_and_integrations() -> None:
    rows = (
        module.Track62BenchmarkRow(
            prompt="Prompt 1",
            baseline_text="baseline completion",
            runtime_text="runtime completion",
            baseline_exact_match=0.0,
            runtime_exact_match=1.0,
            baseline_token_f1=0.25,
            runtime_token_f1=1.0,
            baseline_latency_seconds=0.8,
            runtime_latency_seconds=0.3,
        ),
    )

    report = module.build_track62_evidence_report(
        benchmark_rows=rows,
        docs_present=True,
        dspy_integration_documented=True,
        spacy_llm_integration_documented=True,
    )

    markdown = module.render_track62_evidence_markdown(report, rows)

    assert report.backend_state == "optional"
    assert report.go_no_go == "optional"
    assert report.review_ready is True
    assert report.docs_present is True
    assert "vLLM" in markdown
    assert "optional" in markdown
    assert "DSPy" in markdown
    assert "spaCy-llm" in markdown


def test_track62_compare_runtime_against_baseline() -> None:
    def fake_runtime_completion(prompt: str) -> module.VLLMGenerationResult:
        return module.VLLMGenerationResult(
            prompt=prompt,
            generated_text=f"baseline completion for: {prompt}",
            mode="offline",
            model_name="demo-model",
            elapsed_seconds=0.125,
        )

    report, rows = module.compare_track62_runtime_to_baseline(
        ["Prompt 1"],
        runtime_completion=fake_runtime_completion,
    )

    assert len(rows) == 1
    assert rows[0].runtime_exact_match == 1.0
    assert rows[0].runtime_token_f1 == 1.0
    assert report.go_no_go == "optional"
    assert report.review_ready is True
