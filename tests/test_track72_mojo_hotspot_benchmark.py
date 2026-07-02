"""Tests for the Track 72 Mojo hotspot benchmark harness."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

track72_mojo_hotspot_benchmark = importlib.import_module("track72_mojo_hotspot_benchmark")


def test_track72_benchmark_writes_deferred_evidence_without_mojo(tmp_path: Path) -> None:
    evidence_path = tmp_path / "track72_mojo_hotspot_benchmark.json"

    exit_code = track72_mojo_hotspot_benchmark.main(
        ["--records", "4", "--iterations", "1", "--evidence", str(evidence_path)]
    )
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    results = {result["name"]: result for result in payload["results"]}

    assert exit_code == 0
    assert payload["track"] == "mojo_hotspot_benchmark_20260702"
    assert payload["fixture"]["record_count"] == 4
    assert results["python_json"]["status"] == "measured"
    assert results["orjson_json"]["status"] == "measured"
    assert results["polars_projection"]["status"] in {"measured", "missing_dependency"}
    assert results["mojo_kernel"]["status"] == "missing_dependency"
    assert payload["decision"]["status"] == "deferred"
    assert payload["decision"]["track73"] == "deferred"


def test_track72_benchmark_proceeds_only_when_mojo_beats_fastest_baseline(monkeypatch, tmp_path: Path) -> None:
    evidence_path = tmp_path / "track72_mojo_hotspot_benchmark.json"

    def fake_measure_renderer(name, _renderer, _iterations, *renderer_args, **renderer_kwargs):
        outputs = {
            "python_json": track72_mojo_hotspot_benchmark.BenchmarkResult(
                name="python_json",
                status="measured",
                iterations=1,
                duration_seconds=0.005,
                avg_ms=5.0,
                p95_ms=5.0,
                peak_kib=10.0,
                output_bytes=20,
                output_md5="a" * 32,
                output_sha256="b" * 64,
                error=None,
            ),
            "orjson_json": track72_mojo_hotspot_benchmark.BenchmarkResult(
                name="orjson_json",
                status="measured",
                iterations=1,
                duration_seconds=0.003,
                avg_ms=3.0,
                p95_ms=3.0,
                peak_kib=8.0,
                output_bytes=20,
                output_md5="c" * 32,
                output_sha256="d" * 64,
                error=None,
            ),
            "polars_projection": track72_mojo_hotspot_benchmark.BenchmarkResult(
                name="polars_projection",
                status="measured",
                iterations=1,
                duration_seconds=0.006,
                avg_ms=6.0,
                p95_ms=6.0,
                peak_kib=11.0,
                output_bytes=20,
                output_md5="e" * 32,
                output_sha256="f" * 64,
                error=None,
            ),
            "mojo_kernel": track72_mojo_hotspot_benchmark.BenchmarkResult(
                name="mojo_kernel",
                status="measured",
                iterations=1,
                duration_seconds=0.002,
                avg_ms=2.0,
                p95_ms=2.0,
                peak_kib=7.0,
                output_bytes=20,
                output_md5="g" * 32,
                output_sha256="h" * 64,
                error=None,
            ),
        }
        return outputs[name]

    monkeypatch.setattr(track72_mojo_hotspot_benchmark.shutil, "which", lambda _name: "mojo")
    monkeypatch.setattr(
        track72_mojo_hotspot_benchmark,
        "render_mojo_json",
        lambda tokens, *, workdir: track72_mojo_hotspot_benchmark.render_python_json(tokens),
    )
    monkeypatch.setattr(track72_mojo_hotspot_benchmark, "measure_renderer", fake_measure_renderer)

    payload = track72_mojo_hotspot_benchmark.build_evidence(record_count=4, iterations=1)

    assert payload["decision"]["status"] == "proceed"
    assert payload["decision"]["track73"] == "proceed"
    assert payload["decision"]["comparison"]["best_non_mojo"] == "orjson_json"
    assert payload["decision"]["comparison"]["speedup_ratio"] == pytest.approx(2.0 / 3.0)
