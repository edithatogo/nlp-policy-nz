#!/usr/bin/env python
"""Benchmark extraction manifest rendering and table export runtimes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import msgspec
import orjson

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nlp_policy_nz.extraction import (  # noqa: E402
    ExtractionManifest,
    extraction_manifest_from_pipeline_records,
    render_extraction_manifest_json,
)
from nlp_policy_nz.storage import PipelineRecord  # noqa: E402


def _make_pipeline_records(record_count: int) -> list[PipelineRecord]:
    """Build representative pipeline records with several extraction families."""
    records: list[PipelineRecord] = []
    for index in range(record_count):
        text = (
            f"A person must apply before 1 July 2026. The agency may approve "
            f"the application for example record {index}."
        )
        records.append(
            PipelineRecord(
                doc_id=f"example-{index:05d}",
                corpus_source="legislation",
                raw_text=text,
                cleaned_tokens=text.split(),
                nz_act_citations=[f"nz/statutes/example-act/2026/{index}"],
                te_reo_terms=[],
                deontic_modality=[
                    {"label": "obligation", "text": "must apply"},
                    {"label": "permission", "text": "may approve"},
                ],
                temporal_expressions=[
                    {"type": "DATE", "text": "1 July 2026", "value": "2026-07-01"}
                ],
                resolved_entities=[
                    {"text": "agency", "label": "CROWN_ENTITY", "qid": f"Q{1000 + index}"}
                ],
                amendments=[{"type": "insert", "text": "insert example clause"}],
                legal_effect="obligation",
            )
        )
    return records


def _percentile_95(values: list[float]) -> float:
    """Return the 95th percentile for a short timing series."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, round(0.95 * (len(ordered) - 1)))
    return ordered[index]


def _result(
    name: str,
    timings: list[float],
    output: bytes,
    *,
    status: str = "measured",
    error: str | None = None,
) -> dict[str, Any]:
    total = sum(timings)
    avg = total / len(timings) if timings else 0.0
    return {
        "name": name,
        "status": status,
        "iterations": len(timings),
        "duration_seconds": round(total, 6),
        "avg_ms": round(avg * 1000, 6),
        "p95_ms": round(_percentile_95(timings) * 1000, 6),
        "output_bytes": len(output),
        "output_md5": hashlib.md5(output, usedforsecurity=False).hexdigest() if output else "",
        "error": error,
    }


def _time_renderer(
    name: str,
    renderer: Callable[[ExtractionManifest], str | bytes],
    manifest: ExtractionManifest,
    iterations: int,
) -> dict[str, Any]:
    timings: list[float] = []
    output = b""
    for _ in range(iterations):
        started = time.perf_counter()
        rendered = renderer(manifest)
        timings.append(time.perf_counter() - started)
        output = rendered if isinstance(rendered, bytes) else rendered.encode("utf-8")
    return _result(name, timings, output)


def _stdlib_json(manifest: ExtractionManifest) -> str:
    return json.dumps(
        manifest.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _pydantic_json(manifest: ExtractionManifest) -> str:
    return manifest.model_dump_json()


def _msgspec_json(manifest: ExtractionManifest) -> bytes:
    return msgspec.json.encode(manifest.model_dump(mode="json"))


def _orjson_direct(manifest: ExtractionManifest) -> bytes:
    return orjson.dumps(manifest.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS)


def _table_export_result(manifest: ExtractionManifest, iterations: int) -> dict[str, Any]:
    """Benchmark optional Polars table materialisation from manifest records."""
    try:
        import polars as pl
    except ImportError as exc:  # pragma: no cover - dependency-gated path
        return _result(
            "polars_table",
            [],
            b"",
            status="missing_dependency",
            error=f"polars is not installed: {exc}",
        )

    rows = [
        {
            "record_id": record.record_id,
            "family": record.family.value,
            "label": record.label,
            "citation_path": record.source_trace.citation_path,
            "source_sha256": record.source_trace.source_sha256,
        }
        for record in manifest.records
    ]
    timings: list[float] = []
    output = b""
    for _ in range(iterations):
        started = time.perf_counter()
        frame = pl.DataFrame(rows)
        output = frame.write_json().encode("utf-8")
        timings.append(time.perf_counter() - started)
    return _result("polars_table", timings, output)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=250)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path(".tmp/track56_extraction_manifest_runtime.json"),
        help="Where to write benchmark evidence JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark and write evidence JSON."""
    args = _build_parser().parse_args(argv)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    iterations = max(1, args.iterations)
    pipeline_records = _make_pipeline_records(max(1, args.records))
    manifest = extraction_manifest_from_pipeline_records(
        pipeline_records,
        retrieved_at="2026-06-30T00:00:00Z",
    )

    evidence = {
        "track": "rust_accelerated_extraction_runtime_20260630",
        "experiment": "extraction_manifest_runtime",
        "pipeline_records": len(pipeline_records),
        "extraction_records": len(manifest.records),
        "iterations": iterations,
        "results": [
            _time_renderer("stdlib_json", _stdlib_json, manifest, iterations),
            _time_renderer("pydantic_model_dump_json", _pydantic_json, manifest, iterations),
            _time_renderer("msgspec_json", _msgspec_json, manifest, iterations),
            _time_renderer("orjson_helper", render_extraction_manifest_json, manifest, iterations),
            _time_renderer("orjson_direct", _orjson_direct, manifest, iterations),
            _table_export_result(manifest, iterations),
        ],
    }
    args.evidence.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"wrote evidence to {args.evidence}")  # noqa: T201
    for result in evidence["results"]:
        print(f"{result['name']}: {result['status']}")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
