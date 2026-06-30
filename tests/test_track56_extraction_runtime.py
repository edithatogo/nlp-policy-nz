"""Tests for Track 56 extraction runtime benchmark contracts."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

benchmark_extraction_manifest_runtime = importlib.import_module(
    "benchmark_extraction_manifest_runtime"
)


def test_extraction_manifest_runtime_benchmark_writes_evidence(tmp_path: Path) -> None:
    evidence_path = tmp_path / "track56_extraction_manifest_runtime.json"

    exit_code = benchmark_extraction_manifest_runtime.main(
        ["--records", "3", "--iterations", "1", "--evidence", str(evidence_path)]
    )
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    results = {result["name"]: result for result in payload["results"]}

    assert exit_code == 0
    assert payload["experiment"] == "extraction_manifest_runtime"
    assert payload["pipeline_records"] == 3
    assert payload["extraction_records"] == 24
    assert results["stdlib_json"]["status"] == "measured"
    assert results["pydantic_model_dump_json"]["status"] == "measured"
    assert results["msgspec_json"]["status"] == "measured"
    assert results["orjson_helper"]["status"] == "measured"
    assert results["orjson_direct"]["status"] == "measured"
    assert results["polars_table"]["status"] in {"measured", "missing_dependency"}


def test_track56_runtime_policy_documents_dependency_and_ffi_boundaries() -> None:
    runtime_doc = (ROOT / "docs" / "extraction-runtime.md").read_text(encoding="utf-8")
    evidence = json.loads(
        (ROOT / "artifacts" / "track56" / "extraction_manifest_runtime_50.json").read_text(
            encoding="utf-8"
        )
    )

    assert "Pydantic 2 for public manifest schemas" in runtime_doc
    assert "`orjson` for deterministic JSON output" in runtime_doc
    assert "Polars/Arrow projections" in runtime_doc
    assert "Future FFI Boundary" in runtime_doc
    assert "`PipelineRecord` objects" in runtime_doc
    assert "Pydantic model instances" in runtime_doc
    assert evidence["experiment"] == "extraction_manifest_runtime"
    assert evidence["extraction_records"] == 400
