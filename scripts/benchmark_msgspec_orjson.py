#!/usr/bin/env python
"""Benchmark stdlib JSON, msgspec, and orjson serializers."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

Record = dict[str, Any]
Serializer = Callable[[list[Record]], bytes]


def _make_records(record_count: int) -> list[Record]:
    base_paragraph = (
        "Clause 1: The legal entity shall operate in good faith and keep records "
        "for audit and review. Clause 2: Any data export must preserve IDs and "
        "timestamps to permit traceability across jurisdictions."
    )
    records: list[Record] = []
    for index in range(record_count):
        records.append(
            {
                "doc_id": f"doc-{index:05d}",
                "corpus_source": "test-corpus",
                "raw_text": f"{base_paragraph} ({index})",
                "cleaned_tokens": base_paragraph.split(),
                "citations": [f"CIT-{index:04d}", f"CIT-{index + 1:04d}"],
                "te_reo_terms": ["mana", "taonga"],
                "embeddings": [float(index % 17) / 17.0, float((index + 1) % 29) / 29.0],
                "deontic_modality": None,
                "temporal_expressions": [f"2026-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}"],
                "resolved_metadata": {"source": "benchmark", "index": index},
            }
        )
    return records


def _serialize_stdlib(payload: list[Record]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _serialize_msgspec(payload: list[Record]) -> bytes:
    try:
        import msgspec
    except ImportError as exc:  # pragma: no cover - exercised in optional path only
        raise RuntimeError("msgspec is not installed") from exc

    return msgspec.json.encode(payload)


def _serialize_orjson(payload: list[Record]) -> bytes:
    try:
        import orjson
    except ImportError as exc:  # pragma: no cover - exercised in optional path only
        raise RuntimeError("orjson is not installed") from exc

    return orjson.dumps(payload)


@dataclass(frozen=True)
class SerializerResult:
    """Benchmark result for one serializer."""

    status: str
    iterations: int
    duration_seconds: float
    avg_ms: float
    p95_ms: float
    throughput_mb_s: float
    output_bytes: int
    output_md5: str
    parity_with_stdlib_bytes: bool | None
    parity_with_stdlib_payload: bool | None
    peak_memory_bytes: int
    error: str | None = None


def _percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    index = max(0, round(0.95 * (len(values_sorted) - 1)))
    return values_sorted[index]


def _run_benchmark(
    serializer: Serializer,
    payload: list[Record],
    iterations: int,
    stdlib_reference: bytes | None,
    stdlib_payload: list[Record] | None,
) -> SerializerResult:
    timings: list[float] = []
    output_bytes = 0
    output_md5 = ""
    parity_bytes: bool | None = None
    parity_payload: bool | None = None
    peak_memory = 0

    for _ in range(iterations):
        tracemalloc.start()
        start = time.perf_counter()
        encoded = serializer(payload)
        timings.append(time.perf_counter() - start)
        _, run_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        output_bytes += len(encoded)
        peak_memory = max(peak_memory, run_peak)
        if output_md5 == "":
            output_md5 = hashlib.md5(encoded, usedforsecurity=False).hexdigest()
        if stdlib_reference is not None and parity_bytes is None:
            parity_bytes = len(encoded) == len(stdlib_reference)
        if stdlib_payload is not None and parity_payload is None:
            try:
                parity_payload = json.loads(encoded.decode("utf-8")) == stdlib_payload
            except Exception:
                parity_payload = False

    total = sum(timings)
    avg_seconds = total / iterations
    throughput_mb_s = (
        ((output_bytes / iterations) / 1024 / 1024) / avg_seconds if avg_seconds else 0.0
    )

    return SerializerResult(
        status="measured",
        iterations=iterations,
        duration_seconds=round(total, 6),
        avg_ms=round(avg_seconds * 1000, 6),
        p95_ms=round(_percentile_95(timings) * 1000, 6),
        throughput_mb_s=round(throughput_mb_s, 6),
        output_bytes=output_bytes // iterations,
        output_md5=output_md5,
        parity_with_stdlib_bytes=parity_bytes if stdlib_reference is not None else None,
        parity_with_stdlib_payload=parity_payload if stdlib_reference is not None else None,
        peak_memory_bytes=peak_memory,
    )


def _missing_result(iterations: int, error: str) -> SerializerResult:
    """Return a placeholder result for an unavailable optional serializer."""
    return SerializerResult(
        status="missing_dependency",
        iterations=iterations,
        duration_seconds=0.0,
        avg_ms=0.0,
        p95_ms=0.0,
        throughput_mb_s=0.0,
        output_bytes=0,
        output_md5="",
        parity_with_stdlib_bytes=None,
        parity_with_stdlib_payload=None,
        peak_memory_bytes=0,
        error=error,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=1_000)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument(
        "--evidence",
        default=Path(".tmp/track14_msgspec_orjson_benchmark.json"),
        type=Path,
        help="Where to write benchmark evidence JSON.",
    )
    return parser


def _run_optional_serializer(
    name: str,
    module_name: str,
    serializer: Serializer,
    payload: list[Record],
    iterations: int,
    stdlib_reference: bytes,
) -> SerializerResult:
    if importlib.util.find_spec(module_name) is None:
        return _missing_result(iterations, f"{module_name} is not installed")
    try:
        return _run_benchmark(serializer, payload, iterations, stdlib_reference, payload)
    except RuntimeError as exc:  # pragma: no cover - optional dependency path
        return _missing_result(iterations, str(exc))
    except Exception as exc:  # pragma: no cover - defensive benchmark path
        return _missing_result(iterations, f"{name} benchmark failed: {exc}")


def main(argv: list[str] | None = None) -> int:
    """Run the serializer benchmark and write evidence."""
    args = _build_parser().parse_args(argv)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)

    iterations = max(1, args.iterations)
    payload = _make_records(max(1, args.records))
    stdlib_reference = _serialize_stdlib(payload)
    stdlib_result = _run_benchmark(_serialize_stdlib, payload, iterations, None, None)
    msgspec_result = _run_optional_serializer(
        "msgspec_json",
        "msgspec",
        _serialize_msgspec,
        payload,
        iterations,
        stdlib_reference,
    )
    orjson_result = _run_optional_serializer(
        "orjson",
        "orjson",
        _serialize_orjson,
        payload,
        iterations,
        stdlib_reference,
    )

    evidence = {
        "track": "rust_backed_tooling_hotpaths_20260614",
        "experiment": "msgspec_orjson_serializer",
        "records": len(payload),
        "iterations": iterations,
        "results": [
            {"name": "stdlib_json", **asdict(stdlib_result)},
            {"name": "msgspec_json", **asdict(msgspec_result)},
            {"name": "orjson", **asdict(orjson_result)},
        ],
    }
    args.evidence.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"wrote evidence to {args.evidence}")  # noqa: T201
    for result in evidence["results"]:
        print(f"{result['name']}: {result['status']}")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
