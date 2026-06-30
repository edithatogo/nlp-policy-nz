"""Tests for the Track 23 msgspec vs pydantic benchmark contract."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKDIR = ROOT / ".tmp" / "track23-tests"
EVIDENCE = ROOT / "artifacts" / "track23" / "pydantic_vs_msgspec_pipeline_record_128.json"
sys.path.insert(0, str(ROOT / "scripts"))

benchmark_pipeline_record = importlib.import_module("benchmark_pipeline_record_msgspec_pydantic")


def _evidence_path(filename: str) -> Path:
    """Return a writable evidence path for benchmark outputs."""
    WORKDIR.mkdir(parents=True, exist_ok=True)
    return WORKDIR / filename


def test_pipeline_record_benchmark_records_msgspec_and_pydantic_results() -> None:
    """The benchmark should write measured results for both libraries."""
    evidence_path = _evidence_path("track23_pydantic_vs_msgspec_benchmark.json")

    exit_code = benchmark_pipeline_record.main(
        ["--records", "8", "--iterations", "2", "--evidence", str(evidence_path)]
    )
    assert exit_code == 0

    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    results = {entry["name"]: entry["status"] for entry in payload["results"]}

    assert payload["experiment"] == "pydantic_vs_msgspec_pipeline_record"
    assert results["msgspec"] == "measured"
    assert results["pydantic_v2"] == "measured"


def test_checked_in_pipeline_record_benchmark_evidence_is_complete() -> None:
    """The durable Track 23 evidence artifact records both benchmark lanes."""
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    results = {entry["name"]: entry for entry in payload["results"]}

    assert payload["records"] == 128
    assert payload["iterations"] == 10
    assert results["msgspec"]["status"] == "measured"
    assert results["pydantic_v2"]["status"] == "measured"
    assert results["msgspec"]["output_md5"] == results["pydantic_v2"]["output_md5"]
