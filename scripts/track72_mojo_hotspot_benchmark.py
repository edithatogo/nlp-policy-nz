#!/usr/bin/env python
"""Benchmark a deterministic hotspot candidate for the Mojo migration track.

The candidate fixture is a token-normalization / modal-term scan over a
reproducible legislation-like text slice. The script compares:

- a pure Python scan plus stdlib JSON rendering;
- the same Python scan plus Rust-backed `orjson`;
- a Polars projection over the token stream; and
- an optional Mojo kernel, when the `mojo` executable is present.

The generated evidence is intended to be small enough to run in GitHub Actions
while still capturing input/output hashes, environment metadata, timings, and a
go/no-go decision for the next track.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import orjson

try:
    import polars as pl
except ImportError:  # pragma: no cover - optional in some runners
    pl = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE = ROOT / ".tmp" / "track72_mojo_hotspot_benchmark.json"
DEFAULT_ITERATIONS = 3
DEFAULT_RECORDS = 240

TOKEN_SENTENCE = (
    "The Minister must publish the notice, the agency may consult the committee, "
    "and the authority shall report the outcome."
)


@dataclass(frozen=True)
class BenchmarkResult:
    """Timing and parity evidence for one renderer."""

    name: str
    status: str
    iterations: int
    duration_seconds: float
    avg_ms: float
    p95_ms: float
    peak_kib: float
    output_bytes: int
    output_md5: str
    output_sha256: str
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return asdict(self)


def build_token_fixture(record_count: int) -> list[str]:
    """Build a deterministic modal-token fixture."""
    tokens: list[str] = []
    seed_tokens = TOKEN_SENTENCE.lower().replace(",", "").replace(".", "").split()
    for index in range(record_count):
        tokens.extend(seed_tokens)
        tokens.append(f"record-{index}")
    return tokens


def summarize_tokens(tokens: list[str]) -> dict[str, Any]:
    """Compute a deterministic summary for the token fixture."""
    modal_positions = [index for index, token in enumerate(tokens) if token in {"must", "may", "shall"}]
    modal_counts = {
        "must": sum(1 for token in tokens if token == "must"),
        "may": sum(1 for token in tokens if token == "may"),
        "shall": sum(1 for token in tokens if token == "shall"),
    }
    checksum = sum(modal_positions) + len(tokens) + sum(modal_counts.values())
    return {
        "token_count": len(tokens),
        "modal_counts": modal_counts,
        "modal_positions": modal_positions,
        "checksum": checksum,
    }


def render_python_json(tokens: list[str]) -> str:
    """Render the summary through stdlib JSON."""
    return json.dumps(summarize_tokens(tokens), indent=2, sort_keys=True)


def render_orjson(tokens: list[str]) -> bytes:
    """Render the summary through Rust-backed orjson."""
    return orjson.dumps(summarize_tokens(tokens), option=orjson.OPT_SORT_KEYS)


def render_polars_json(tokens: list[str]) -> str:
    """Render the summary through a Polars projection."""
    if pl is None:
        raise RuntimeError("polars is not installed")
    frame = pl.DataFrame(
        {
            "token": tokens,
            "is_modal": [token in {"must", "may", "shall"} for token in tokens],
        }
    )
    modal_rows = frame.filter(pl.col("is_modal")).select("token").to_series().to_list()
    modal_counts = {
        "must": modal_rows.count("must"),
        "may": modal_rows.count("may"),
        "shall": modal_rows.count("shall"),
    }
    summary = {
        "token_count": frame.height,
        "modal_counts": modal_counts,
        "modal_positions": [index for index, token in enumerate(tokens) if token in {"must", "may", "shall"}],
        "checksum": sum(index for index, token in enumerate(tokens) if token in {"must", "may", "shall"})
        + frame.height
        + sum(modal_counts.values()),
    }
    return json.dumps(summary, indent=2, sort_keys=True)


def render_mojo_json(tokens: list[str], *, workdir: Path) -> str:
    """Render the summary via a generated Mojo kernel.

    The kernel is intentionally tiny and deterministic. It is generated from the
    Python fixture so GitHub Actions can benchmark the same token stream without
    checking in large source blobs.
    """
    mojo = shutil.which("mojo")
    if mojo is None:
        raise FileNotFoundError("mojo executable is not available")
    mojo_source = workdir / "track72_modal_scan.mojo"
    mojo_source.write_text(_build_mojo_source(tokens), encoding="utf-8")
    completed = subprocess.run(
        [mojo, str(mojo_source)],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def measure_renderer(name: str, renderer, iterations: int, *renderer_args, **renderer_kwargs) -> BenchmarkResult:
    """Benchmark a renderer and record timing plus output hashes."""
    timings: list[float] = []
    output_text = ""
    peak_kib = 0.0
    error: str | None = None
    status = "measured"
    for _ in range(iterations):
        tracemalloc.start()
        started = time.perf_counter()
        try:
            rendered = renderer(*renderer_args, **renderer_kwargs)
        except Exception as exc:  # pragma: no cover - dependency-gated path
            tracemalloc.stop()
            status = "missing_dependency"
            error = str(exc)
            output_text = ""
            timings = []
            break
        duration = time.perf_counter() - started
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        timings.append(duration)
        peak_kib = max(peak_kib, peak / 1024)
        output_text = rendered.decode("utf-8") if isinstance(rendered, bytes) else rendered

    if timings:
        ordered = sorted(timings)
        p95 = ordered[min(len(ordered) - 1, round(0.95 * (len(ordered) - 1)))]
        avg = sum(timings) / len(timings)
        duration_seconds = sum(timings)
    else:
        p95 = 0.0
        avg = 0.0
        duration_seconds = 0.0

    normalized_output = output_text.encode("utf-8")
    return BenchmarkResult(
        name=name,
        status=status,
        iterations=len(timings),
        duration_seconds=round(duration_seconds, 6),
        avg_ms=round(avg * 1000, 6),
        p95_ms=round(p95 * 1000, 6),
        peak_kib=round(peak_kib, 3),
        output_bytes=len(normalized_output),
        output_md5=hashlib.md5(normalized_output, usedforsecurity=False).hexdigest() if normalized_output else "",
        output_sha256=hashlib.sha256(normalized_output).hexdigest() if normalized_output else "",
        error=error,
    )


def _build_mojo_source(tokens: list[str]) -> str:
    token_literals = ", ".join(f'"{token}"' for token in tokens)
    return f"""from std.collections.string import String
from std.collections import List

def main():
    var tokens: List[String] = [{token_literals}]
    var must_count: Int = 0
    var may_count: Int = 0
    var shall_count: Int = 0
    var modal_positions: List[Int] = List[Int]()

    for index in range(len(tokens)):
        var token = tokens[index]
        if token == "must":
            must_count += 1
            modal_positions.append(index)
            print(t"modal_position={{index}}")
        elif token == "may":
            may_count += 1
            modal_positions.append(index)
            print(t"modal_position={{index}}")
        elif token == "shall":
            shall_count += 1
            modal_positions.append(index)
            print(t"modal_position={{index}}")

    var checksum: Int = 0
    for position in modal_positions:
        checksum += position
    checksum += len(tokens) + must_count + may_count + shall_count

    print(t"token_count={{len(tokens)}}")
    print(t"must_count={{must_count}}")
    print(t"may_count={{may_count}}")
    print(t"shall_count={{shall_count}}")
    print(t"checksum={{checksum}}")
"""


def _parse_mojo_output(rendered: str) -> str:
    try:
        payload_json = json.loads(rendered)
    except json.JSONDecodeError:
        payload_json = None
    else:
        if isinstance(payload_json, dict) and {
            "token_count",
            "modal_counts",
            "modal_positions",
            "checksum",
        }.issubset(payload_json):
            return json.dumps(payload_json, indent=2, sort_keys=True)

    payload: dict[str, Any] = {}
    modal_positions: list[int] = []
    for line in rendered.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key == "modal_position":
            modal_positions.append(int(value))
            continue
        payload[key] = int(value)
    modal_counts = {key: payload[key] for key in ("must_count", "may_count", "shall_count")}
    summary = {
        "token_count": payload.get("token_count", 0),
        "modal_counts": {
            "must": modal_counts["must_count"],
            "may": modal_counts["may_count"],
            "shall": modal_counts["shall_count"],
        },
        "modal_positions": modal_positions,
        "checksum": payload.get("checksum", 0),
    }
    return json.dumps(summary, indent=2, sort_keys=True)


def _best_non_mojo_result(results: list[BenchmarkResult]) -> BenchmarkResult | None:
    """Return the fastest measured non-Mojo renderer, if any."""
    measured = [result for result in results if result.status == "measured" and result.name != "mojo_kernel"]
    if not measured:
        return None
    return min(measured, key=lambda result: result.avg_ms)


def build_evidence(*, record_count: int, iterations: int) -> dict[str, Any]:
    """Build benchmark evidence for the Track 72 candidate."""
    tokens = build_token_fixture(record_count)
    input_payload = json.dumps(tokens, separators=(",", ":"), ensure_ascii=False)
    input_hash = hashlib.sha256(input_payload.encode("utf-8")).hexdigest()
    with tempfile.TemporaryDirectory(prefix="track72_mojo_") as tmpdir:
        workdir = Path(tmpdir)
        results = [
            measure_renderer("python_json", render_python_json, iterations, tokens),
            measure_renderer("orjson_json", render_orjson, iterations, tokens),
            measure_renderer("polars_projection", render_polars_json, iterations, tokens),
        ]
        mojo_path = shutil.which("mojo")
        if mojo_path is None:
            results.append(
                BenchmarkResult(
                    name="mojo_kernel",
                    status="missing_dependency",
                    iterations=0,
                    duration_seconds=0.0,
                    avg_ms=0.0,
                    p95_ms=0.0,
                    peak_kib=0.0,
                    output_bytes=0,
                    output_md5="",
                    output_sha256="",
                    error="mojo executable is not available",
                )
            )
            decision = {
                "status": "deferred",
                "track73": "deferred",
                "reason": "Mojo is not installed in the current runtime, so the benchmark remains a baseline-and-parity decision record.",
            }
        else:
            mojo_rendered = render_mojo_json(tokens, workdir=workdir)
            mojo_summary = json.loads(_parse_mojo_output(mojo_rendered))
            baseline_summary = json.loads(render_python_json(tokens))
            if mojo_summary != baseline_summary:
                raise RuntimeError("Mojo output does not match the Python baseline summary")
            results.append(
                measure_renderer("mojo_kernel", render_mojo_json, iterations, tokens, workdir=workdir)
            )
            best_baseline = _best_non_mojo_result(results)
            if best_baseline is None:
                raise RuntimeError("No baseline result available for Mojo comparison")
            speedup_ratio = results[-1].avg_ms / best_baseline.avg_ms if best_baseline.avg_ms else float("inf")
            decision = {
                "status": "proceed" if speedup_ratio <= 0.9 else "defer",
                "track73": "proceed" if speedup_ratio <= 0.9 else "deferred",
                "threshold": 0.9,
                "comparison": {
                    "best_non_mojo": best_baseline.name,
                    "best_non_mojo_avg_ms": best_baseline.avg_ms,
                    "mojo_avg_ms": results[-1].avg_ms,
                    "speedup_ratio": round(speedup_ratio, 6),
                },
                "reason": (
                    "Mojo matched parity and beat the fastest non-Mojo baseline by at least 10%."
                    if speedup_ratio <= 0.9
                    else "Mojo parity passed but it did not clear the 10% promotion threshold against the fastest non-Mojo baseline."
                ),
            }

    baseline_summary = json.loads(render_python_json(tokens))
    return {
        "track": "mojo_hotspot_benchmark_20260702",
        "fixture": {
            "record_count": record_count,
            "token_count": len(tokens),
            "input_sha256": input_hash,
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "lockfile_hash": _lockfile_hash(),
        },
        "baseline_summary": baseline_summary,
        "results": [result.to_dict() for result in results],
        "decision": decision,
    }


def _lockfile_hash() -> str:
    """Hash the current environment lockfile, preferring uv.lock over pixi.lock."""
    for filename in ("uv.lock", "pixi.lock"):
        path = ROOT / filename
        if path.is_file():
            return hashlib.sha256(path.read_bytes()).hexdigest()
    return ""


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=DEFAULT_RECORDS)
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark and write its evidence JSON."""
    args = build_parser().parse_args(argv)
    evidence = build_evidence(record_count=max(1, args.records), iterations=max(1, args.iterations))
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote evidence to {args.evidence}")  # noqa: T201
    for result in evidence["results"]:
        print(f"{result['name']}: {result['status']}")  # noqa: T201
    print(f"decision: {evidence['decision']['status']}")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
