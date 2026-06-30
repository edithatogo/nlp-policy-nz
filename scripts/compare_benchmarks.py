"""Compare pytest-benchmark JSON output against committed baselines."""

from __future__ import annotations

import argparse
import html
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_THRESHOLD = 0.10


@dataclass(frozen=True, slots=True)
class BenchmarkDelta:
    """One benchmark comparison result."""

    fullname: str
    baseline_mean: float
    current_mean: float
    threshold: float
    status: str

    @property
    def delta_ratio(self) -> float:
        """Return current-vs-baseline mean delta as a ratio."""
        if self.baseline_mean == 0:
            return 0.0
        return (self.current_mean - self.baseline_mean) / self.baseline_mean

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready comparison data."""
        return {
            "fullname": self.fullname,
            "baseline_mean": self.baseline_mean,
            "current_mean": self.current_mean,
            "delta_ratio": self.delta_ratio,
            "delta_percent": self.delta_ratio * 100,
            "threshold": self.threshold,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class ThresholdConfig:
    """Benchmark threshold configuration."""

    default_threshold: float
    thresholds: dict[str, float]


def load_benchmark_means(path: Path) -> dict[str, float]:
    """Load benchmark mean timings keyed by pytest benchmark fullname."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    means: dict[str, float] = {}
    for benchmark in payload.get("benchmarks", []):
        fullname = str(benchmark["fullname"])
        means[fullname] = float(benchmark["stats"]["mean"])
    if not means:
        raise ValueError(f"no benchmark means found in {path}")
    return means


def load_threshold_config(
    path: Path | None,
    *,
    fallback_default: float = DEFAULT_THRESHOLD,
) -> ThresholdConfig:
    """Load default and per-test thresholds from JSON."""
    if path is None:
        return ThresholdConfig(fallback_default, {})
    payload = json.loads(path.read_text(encoding="utf-8"))
    thresholds = payload.get("thresholds", payload)
    return ThresholdConfig(
        default_threshold=float(payload.get("default_threshold", fallback_default)),
        thresholds={str(key): float(value) for key, value in thresholds.items()},
    )


def compare_benchmarks(
    baseline: dict[str, float],
    current: dict[str, float],
    *,
    thresholds: dict[str, float] | None = None,
    default_threshold: float = DEFAULT_THRESHOLD,
) -> tuple[BenchmarkDelta, ...]:
    """Compare benchmark means and mark missing, new, passed, and regressed tests."""
    threshold_map = thresholds or {}
    names = sorted(set(baseline) | set(current))
    results: list[BenchmarkDelta] = []
    for name in names:
        threshold = threshold_map.get(name, default_threshold)
        if name not in baseline:
            results.append(BenchmarkDelta(name, 0.0, current[name], threshold, "new"))
            continue
        if name not in current:
            results.append(BenchmarkDelta(name, baseline[name], 0.0, threshold, "missing"))
            continue
        delta = BenchmarkDelta(name, baseline[name], current[name], threshold, "passed")
        status = "regressed" if delta.delta_ratio > threshold else "passed"
        results.append(
            BenchmarkDelta(name, baseline[name], current[name], threshold, status)
        )
    return tuple(results)


def comparison_summary(results: tuple[BenchmarkDelta, ...]) -> dict[str, Any]:
    """Return aggregate pass/fail counts for comparison results."""
    status_counts: dict[str, int] = {}
    for result in results:
        status_counts[result.status] = status_counts.get(result.status, 0) + 1
    return {
        "benchmark_count": len(results),
        "status_counts": status_counts,
        "failed": any(result.status in {"missing", "regressed"} for result in results),
    }


def write_json_report(results: tuple[BenchmarkDelta, ...], path: Path) -> None:
    """Write a machine-readable comparison report."""
    payload = {
        "summary": comparison_summary(results),
        "benchmarks": [result.to_dict() for result in results],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_html_report(results: tuple[BenchmarkDelta, ...], path: Path) -> None:
    """Write a compact HTML benchmark comparison report."""
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(result.fullname)}</td>"
        f"<td>{result.baseline_mean:.6f}</td>"
        f"<td>{result.current_mean:.6f}</td>"
        f"<td>{result.delta_ratio * 100:.2f}%</td>"
        f"<td>{result.threshold * 100:.2f}%</td>"
        f"<td>{html.escape(result.status)}</td>"
        "</tr>"
        for result in results
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Benchmark regression report</title>
</head>
<body>
  <h1>Benchmark regression report</h1>
  <table>
    <thead>
      <tr>
        <th>Benchmark</th>
        <th>Baseline mean seconds</th>
        <th>Current mean seconds</th>
        <th>Delta</th>
        <th>Threshold</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    """Return the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--current", required=True, type=Path)
    parser.add_argument("--thresholds", type=Path)
    parser.add_argument("--default-threshold", type=float)
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--html-report", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run benchmark comparison from CLI arguments."""
    args = build_parser().parse_args(argv)
    threshold_config = load_threshold_config(args.thresholds)
    default_threshold = (
        threshold_config.default_threshold
        if args.default_threshold is None
        else args.default_threshold
    )
    results = compare_benchmarks(
        load_benchmark_means(args.baseline),
        load_benchmark_means(args.current),
        thresholds=threshold_config.thresholds,
        default_threshold=default_threshold,
    )
    if args.json_report:
        write_json_report(results, args.json_report)
    if args.html_report:
        write_html_report(results, args.html_report)
    for result in results:
        sys.stdout.write(
            f"{result.status}: {result.fullname} "
            f"delta={result.delta_ratio * 100:.2f}% threshold={result.threshold * 100:.2f}%\n"
        )
    return 1 if comparison_summary(results)["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
