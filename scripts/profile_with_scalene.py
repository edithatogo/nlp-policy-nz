"""Small Scalene profiling target for Track 23 quality infrastructure."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from nlp_policy_nz.guard import normalize_text
from nlp_policy_nz.storage import PipelineRecord, serialize_to_parquet


def build_profile_records(record_count: int) -> list[PipelineRecord]:
    """Build deterministic records for CPU and memory profiling."""
    base_text = normalize_text("Maaori Act 2024 requires consultation with iwi.")
    return [
        PipelineRecord(
            doc_id=f"profile-{index:06d}",
            corpus_source="profile",
            raw_text=base_text,
            cleaned_tokens=base_text.split(),
            nz_act_citations=["Māori Act 2024"],
            te_reo_terms=["Māori", "iwi"],
        )
        for index in range(record_count)
    ]


def run_profile(record_count: int, output: Path) -> Path:
    """Generate and serialise profile records to exercise core pipeline paths."""
    records = build_profile_records(record_count)
    output.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    result = serialize_to_parquet(records, output)
    elapsed = time.perf_counter() - start
    print(f"wrote={result} records={len(records)} seconds={elapsed:.4f}")  # noqa: T201
    return result


def main(argv: list[str] | None = None) -> int:
    """Run the Track 23 profiling workload."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=1_000)
    parser.add_argument("--output", type=Path, default=Path(".tmp/profile/records.parquet"))
    args = parser.parse_args(argv)

    run_profile(args.records, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
