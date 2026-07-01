"""Tests for Track 42 performance regression gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.compare_benchmarks import (
    compare_benchmarks,
    load_benchmark_means,
    load_threshold_config,
    main,
)

ROOT = Path(__file__).resolve().parents[1]


def _benchmark_payload(mean: float, fullname: str = "tests/benchmarks/test.py::test_fast") -> dict:
    return {
        "benchmarks": [
            {
                "fullname": fullname,
                "name": fullname.rsplit("::", 1)[-1],
                "stats": {"mean": mean, "median": mean, "ops": 1 / mean},
            }
        ]
    }


def test_compare_benchmarks_detects_regression_and_passes_improvement() -> None:
    baseline = {"bench::test": 1.0}

    passed = compare_benchmarks(baseline, {"bench::test": 0.9})
    regressed = compare_benchmarks(baseline, {"bench::test": 1.2})

    assert passed[0].status == "passed"
    assert passed[0].delta_ratio == pytest.approx(-0.1)
    assert regressed[0].status == "regressed"
    assert regressed[0].delta_ratio > 0.1


def test_compare_benchmarks_marks_missing_current_benchmark_as_failure() -> None:
    result = compare_benchmarks({"bench::test": 1.0}, {})

    assert result[0].status == "missing"


def test_compare_benchmark_cli_writes_json_and_html_reports(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    json_report = tmp_path / "report.json"
    html_report = tmp_path / "report.html"
    baseline.write_text(json.dumps(_benchmark_payload(1.0)), encoding="utf-8")
    current.write_text(json.dumps(_benchmark_payload(1.05)), encoding="utf-8")

    exit_code = main(
        [
            "--baseline",
            str(baseline),
            "--current",
            str(current),
            "--json-report",
            str(json_report),
            "--html-report",
            str(html_report),
        ]
    )

    assert exit_code == 0
    assert json.loads(json_report.read_text(encoding="utf-8"))["summary"]["failed"] is False
    assert "<html" in html_report.read_text(encoding="utf-8")


def test_compare_benchmark_cli_fails_on_regression(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    baseline.write_text(json.dumps(_benchmark_payload(1.0)), encoding="utf-8")
    current.write_text(json.dumps(_benchmark_payload(1.2)), encoding="utf-8")

    assert main(["--baseline", str(baseline), "--current", str(current)]) == 1


def test_threshold_config_default_is_used_when_cli_default_is_absent(tmp_path: Path) -> None:
    threshold_path = tmp_path / "thresholds.json"
    threshold_path.write_text(
        json.dumps({"default_threshold": 0.25, "thresholds": {}}),
        encoding="utf-8",
    )

    config = load_threshold_config(threshold_path)
    result = compare_benchmarks(
        {"bench::test": 1.0},
        {"bench::test": 1.2},
        thresholds=config.thresholds,
        default_threshold=config.default_threshold,
    )

    assert config.default_threshold == 0.25
    assert result[0].status == "passed"


def test_track42_baseline_and_threshold_config_are_committed() -> None:
    baseline_path = ROOT / "artifacts" / "baselines" / "pytest-benchmark.json"
    threshold_path = ROOT / "config" / "benchmark_thresholds.json"

    means = load_benchmark_means(baseline_path)
    thresholds = json.loads(threshold_path.read_text(encoding="utf-8"))

    assert "test_process_legislation_throughput_benchmark" in next(iter(means))
    assert thresholds["default_threshold"] == 0.1
    assert set(thresholds["thresholds"]) <= set(means)


def test_track42_workflows_wire_comparison_and_baseline_update() -> None:
    benchmark_workflow = (ROOT / ".github" / "workflows" / "benchmark.yml").read_text(
        encoding="utf-8"
    )
    update_workflow = (ROOT / ".github" / "workflows" / "benchmark-update.yml").read_text(
        encoding="utf-8"
    )

    assert "scripts/compare_benchmarks.py" in benchmark_workflow
    assert "--baseline artifacts/baselines/pytest-benchmark.json" in benchmark_workflow
    assert "benchmark-regression.html" in benchmark_workflow
    assert "branches: [master]" in update_workflow
    assert "artifacts/baselines/pytest-benchmark.json" in update_workflow
    assert "git-auto-commit-action" in update_workflow


def test_track42_pyproject_exposes_regression_config() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "[tool.legal_nz.performance_regression]" in pyproject
    assert 'baseline = "artifacts/baselines/pytest-benchmark.json"' in pyproject
    assert 'thresholds = "config/benchmark_thresholds.json"' in pyproject
