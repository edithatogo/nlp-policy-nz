"""Micro-benchmark harness for pipeline throughput regression tracking."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

from nlp_policy_nz.telemetry.benchmarks import PIPELINE_BENCHMARK_CONTRACT


def test_pipeline_benchmark_evidence_contract_is_fixture_bounded() -> None:
    """Benchmark metadata is explicit about repo-side and external gates."""
    contract = PIPELINE_BENCHMARK_CONTRACT

    assert contract.name == "pipeline.process_legislation.throughput"
    assert contract.corpus_mode == "deterministic-fixture"
    assert contract.requires_pytest_benchmark is True
    assert contract.uses_full_corpus is False
    assert "throughput_docs_per_second" in contract.metrics
    assert any("full Hansard corpus" in gate for gate in contract.external_gates)


@pytest.mark.skipif(
    importlib.util.find_spec("pytest_benchmark") is None,
    reason="pytest-benchmark is not installed",
)
def test_process_legislation_throughput_benchmark(benchmark: Any, monkeypatch, tmp_path) -> None:
    """Benchmark a lightweight legislation pipeline path without model loading."""
    from nlp_policy_nz import pipeline_api

    input_file = tmp_path / "act.txt"
    output_file = tmp_path / "legislation.parquet"
    input_file.write_text("The Minister must report. The agency may consult.", encoding="utf-8")

    class FakeNlp:
        def __init__(self) -> None:
            self.pipe_names: list[str] = []

        def add_pipe(self, *_args: Any, **_kwargs: Any) -> None:
            self.pipe_names.append("deontic_modality")

        def __call__(self, _text: str) -> Any:
            return type("Doc", (), {"ents": [], "spans": {}})()

    def fake_serialize(records: list[Any], out: str | Path) -> Path:
        path = Path(out)
        path.write_text(str(len(records)), encoding="utf-8")
        return path

    monkeypatch.setattr(pipeline_api, "configure_tracing", lambda **_kwargs: None)
    monkeypatch.setattr(pipeline_api, "create_nlp_pipeline", FakeNlp)
    monkeypatch.setattr(pipeline_api, "create_citation_ruler", lambda _nlp: None)
    monkeypatch.setattr(
        pipeline_api,
        "chunk_legislation_document",
        lambda _text, _nlp, year, number: [
            {"doc_id": "doc-1", "text": "The Minister must report."},
            {"doc_id": "doc-2", "text": "The agency may consult."},
        ],
    )
    monkeypatch.setattr(pipeline_api, "_extract_te_reo_terms", lambda _text: [])
    monkeypatch.setattr(pipeline_api, "_extract_citations", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "detect_modality", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "detect_temporal_expressions", lambda _text, _nlp: [])
    monkeypatch.setattr(pipeline_api, "classify_legal_effect", lambda _text, _nlp: None)
    monkeypatch.setattr(pipeline_api, "serialize_to_parquet", fake_serialize)

    result = benchmark(
        pipeline_api.process_legislation,
        input_file,
        output_file,
        False,
    )

    assert result == output_file.resolve()
