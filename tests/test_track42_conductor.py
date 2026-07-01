"""Conductor contract tests for Track 42."""

from __future__ import annotations

import json
from pathlib import Path

TRACK42 = Path("conductor/tracks/archive/track42_performance_regression_20260626")


def test_track42_conductor_registry_and_metadata_are_complete() -> None:
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK42.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK42.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK42.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 42: Performance Regression CI & Benchmark Baselines (archived)" in registry
    assert str(TRACK42).replace("\\", "/") in registry
    assert metadata["track_id"] == "track42_performance_regression_20260626"
    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    assert plan.count("[x]") >= 7
    assert spec.count("[x]") >= 6


def test_track42_evidence_links_all_required_artifacts() -> None:
    evidence = TRACK42.joinpath("evidence.md").read_text(encoding="utf-8")
    required = (
        "artifacts/baselines/pytest-benchmark.json",
        "config/benchmark_thresholds.json",
        "scripts/compare_benchmarks.py",
        ".github/workflows/benchmark.yml",
        ".github/workflows/benchmark-update.yml",
        "docs/perf_regression.md",
        "tests/test_track42_performance_regression.py",
    )

    for path in required:
        assert Path(path).is_file()
        assert path in evidence
