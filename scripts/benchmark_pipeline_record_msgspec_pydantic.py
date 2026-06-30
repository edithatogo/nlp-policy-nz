#!/usr/bin/env python
"""Benchmark msgspec vs pydantic v2 for ``PipelineRecord`` JSON round-trips."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import msgspec
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nlp_policy_nz.storage import PipelineRecord


class PipelineRecordModel(BaseModel):
    """Pydantic v2 mirror of the Track 23 pipeline record schema."""

    model_config = ConfigDict(extra="forbid")

    doc_id: str
    corpus_source: str
    raw_text: str
    cleaned_tokens: list[str]
    nz_act_citations: list[str]
    te_reo_terms: list[str]
    embeddings: list[float] | None = None
    deontic_modality: list[dict[str, str | int | None]] = Field(default_factory=list)
    temporal_expressions: list[dict[str, str | int | None]] = Field(default_factory=list)
    resolved_entities: list[dict[str, Any]] = Field(default_factory=list)
    legal_effect: str | None = None
    voting_record: dict[str, Any] | None = None
    amendments: list[dict[str, Any]] = Field(default_factory=list)
    arguments: list[dict[str, Any]] = Field(default_factory=list)
    argument_label_source: str | None = None
    stance: str | None = None
    stance_label_source: str | None = None
    submitter_name: str | None = None
    committee: str | None = None
    bill_reference: str | None = None
    linkage_confidence: float | None = None
    challenged_regulation: str | None = None
    grounds: str | None = None
    report_title: str | None = None
    findings: list[str] | None = None
    recommendations: list[str] | None = None


BatchAdapter = TypeAdapter(list[PipelineRecordModel])


def _make_records(record_count: int) -> list[dict[str, Any]]:
    """Build a representative batch of pipeline-record-shaped payloads."""
    base_text = (
        "The committee considered the bill and recorded a clear recommendation "
        "for the House. The record also preserves citations, temporal markers, "
        "and stance metadata for downstream analysis."
    )
    records: list[dict[str, Any]] = []
    for index in range(record_count):
        records.append(
            {
                "doc_id": f"record-{index:05d}",
                "corpus_source": "hansard",
                "raw_text": f"{base_text} ({index})",
                "cleaned_tokens": base_text.split(),
                "nz_act_citations": [f"NZ Act {index % 7 + 1:02d}"],
                "te_reo_terms": ["iwi", "mana"],
                "embeddings": [float(index % 13) / 13.0, float((index + 1) % 17) / 17.0],
                "deontic_modality": [{"label": "must", "scope": "committee"}],
                "temporal_expressions": [{"value": "2026-06-29", "kind": "date"}],
                "resolved_entities": [{"qid": f"Q{index + 1000}", "confidence": 0.91}],
                "legal_effect": "obligation",
                "voting_record": {"votes": None, "party_votes": None},
                "amendments": [{"type": "substantive", "section": "1"}],
                "arguments": [{"role": "claim", "text": "policy should proceed"}],
                "argument_label_source": "predicted",
                "stance": "support",
                "stance_label_source": "predicted",
                "submitter_name": "Example Submitter",
                "committee": "Justice Committee",
                "bill_reference": "Bill 123-1",
                "linkage_confidence": 0.82,
                "challenged_regulation": None,
                "grounds": None,
                "report_title": "Example Report",
                "findings": ["Finds the measure workable."],
                "recommendations": ["Recommend enactment."],
            }
        )
    return records


def _percentile_95(values: list[float]) -> float:
    """Return the 95th percentile for a short timing series."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, round(0.95 * (len(ordered) - 1)))
    return ordered[index]


def _run_msgspec_roundtrip(payload: bytes, iterations: int) -> dict[str, Any]:
    """Benchmark msgspec JSON decode/encode over the same payload."""
    decode_timings: list[float] = []
    encode_timings: list[float] = []
    last_encoded = b""
    last_decoded: list[PipelineRecord] = []

    for _ in range(iterations):
        decode_started = time.perf_counter()
        last_decoded = msgspec.json.decode(payload, type=list[PipelineRecord])
        decode_timings.append(time.perf_counter() - decode_started)

        encode_started = time.perf_counter()
        last_encoded = msgspec.json.encode(last_decoded)
        encode_timings.append(time.perf_counter() - encode_started)

    total_decode = sum(decode_timings)
    total_encode = sum(encode_timings)
    total = total_decode + total_encode
    return {
        "status": "measured",
        "iterations": iterations,
        "decode_avg_ms": round((total_decode / iterations) * 1000, 6),
        "decode_p95_ms": round(_percentile_95(decode_timings) * 1000, 6),
        "encode_avg_ms": round((total_encode / iterations) * 1000, 6),
        "encode_p95_ms": round(_percentile_95(encode_timings) * 1000, 6),
        "roundtrip_avg_ms": round((total / iterations) * 1000, 6),
        "roundtrip_p95_ms": round(
            _percentile_95([d + e for d, e in zip(decode_timings, encode_timings, strict=True)])
            * 1000,
            6,
        ),
        "output_bytes": len(last_encoded),
        "output_md5": hashlib.md5(last_encoded, usedforsecurity=False).hexdigest(),
    }


def _run_pydantic_roundtrip(payload: bytes, iterations: int) -> dict[str, Any]:
    """Benchmark pydantic JSON validation/serialisation over the same payload."""
    decode_timings: list[float] = []
    encode_timings: list[float] = []
    last_encoded = b""
    last_decoded: list[PipelineRecordModel] = []

    for _ in range(iterations):
        decode_started = time.perf_counter()
        last_decoded = BatchAdapter.validate_json(payload)
        decode_timings.append(time.perf_counter() - decode_started)

        encode_started = time.perf_counter()
        last_encoded = BatchAdapter.dump_json(last_decoded)
        encode_timings.append(time.perf_counter() - encode_started)

    total_decode = sum(decode_timings)
    total_encode = sum(encode_timings)
    total = total_decode + total_encode
    return {
        "status": "measured",
        "iterations": iterations,
        "decode_avg_ms": round((total_decode / iterations) * 1000, 6),
        "decode_p95_ms": round(_percentile_95(decode_timings) * 1000, 6),
        "encode_avg_ms": round((total_encode / iterations) * 1000, 6),
        "encode_p95_ms": round(_percentile_95(encode_timings) * 1000, 6),
        "roundtrip_avg_ms": round((total / iterations) * 1000, 6),
        "roundtrip_p95_ms": round(
            _percentile_95([d + e for d, e in zip(decode_timings, encode_timings, strict=True)])
            * 1000,
            6,
        ),
        "output_bytes": len(last_encoded),
        "output_md5": hashlib.md5(last_encoded, usedforsecurity=False).hexdigest(),
    }


def _build_parser() -> argparse.ArgumentParser:
    """Return the CLI parser for the benchmark runner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=1_000)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument(
        "--evidence",
        type=Path,
        default=Path(".tmp/track23_pydantic_vs_msgspec_benchmark.json"),
        help="Where to write benchmark evidence JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark and write an evidence JSON file."""
    args = _build_parser().parse_args(argv)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    iterations = max(1, args.iterations)
    records = _make_records(max(1, args.records))
    payload = msgspec.json.encode(records)

    evidence = {
        "track": "quality_tooling_testing_infrastructure_20260613",
        "experiment": "pydantic_vs_msgspec_pipeline_record",
        "records": len(records),
        "payload_bytes": len(payload),
        "iterations": iterations,
        "results": [
            {"name": "msgspec", **_run_msgspec_roundtrip(payload, iterations)},
            {"name": "pydantic_v2", **_run_pydantic_roundtrip(payload, iterations)},
        ],
    }
    args.evidence.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"wrote evidence to {args.evidence}")  # noqa: T201
    for result in evidence["results"]:
        print(f"{result['name']}: {result['status']}")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
