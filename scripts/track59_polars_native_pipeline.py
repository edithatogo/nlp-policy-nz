"""Benchmark the Track 59 Polars-native corpus pipeline boundary."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from statistics import fmean
from typing import Any

import pandas as pd
import polars as pl

from nlp_policy_nz.storage.polars_pipeline import (
    compute_stats_polars,
    load_parquet_polars,
    search_chunks_polars,
)

TRACK_ID = "track59_polars_native_pipeline_20260701"
DEFAULT_OUTPUT = Path(".tmp") / "track59_polars_native_pipeline.json"


def _sample_frame(repetitions: int = 30) -> pd.DataFrame:
    """Return a compact but benchmark-representative corpus frame."""
    base_rows = [
        {
            "doc_id": "leg-001",
            "corpus_source": "legislation",
            "raw_text": "This Act amends the Climate Change Response Act 2002.",
            "nz_act_citations": ["Climate Change Response Act 2002"],
            "te_reo_terms": [],
            "embeddings": [0.1, 0.2, 0.3],
        },
        {
            "doc_id": "leg-002",
            "corpus_source": "legislation",
            "raw_text": "Section 5 of the Education Act applies here.",
            "nz_act_citations": ["Education Act", "Education Act"],
            "te_reo_terms": [],
            "embeddings": [0.4, 0.5, 0.6],
        },
        {
            "doc_id": "han-001",
            "corpus_source": "hansard",
            "raw_text": "The member spoke about Treaty of Waitangi principles.",
            "nz_act_citations": [],
            "te_reo_terms": ["Treaty", "Waitangi", "Treaty"],
            "embeddings": None,
        },
    ]

    rows: list[dict[str, object]] = []
    for index in range(repetitions):
        for row in base_rows:
            copy = dict(row)
            copy["doc_id"] = f"{row['doc_id']}-{index:02d}"
            rows.append(copy)
    return pd.DataFrame(rows)


def _pandas_load_parquet(path: Path) -> pd.DataFrame:
    """Load Parquet through pandas for the baseline comparison."""
    return pd.read_parquet(path)


def _pandas_search_chunks(query: str, df: pd.DataFrame, top_k: int) -> pd.DataFrame:
    """Mirror the legacy pandas search implementation for benchmarking."""
    if not query.strip():
        return pd.DataFrame(columns=["doc_id", "corpus_source", "raw_text", "relevance"])

    query_lower = query.lower()
    mask = df["raw_text"].str.lower().str.contains(query_lower, na=False)
    matches = df[mask].head(top_k).copy()
    if matches.empty:
        return matches.reindex(columns=["doc_id", "corpus_source", "raw_text", "relevance"])

    matches["relevance"] = (
        matches["raw_text"]
        .str.lower()
        .apply(lambda text: text.count(query_lower) / max(len(text.split()), 1))
    )
    return matches[["doc_id", "corpus_source", "raw_text", "relevance"]].sort_values(
        "relevance",
        ascending=False,
    )


def _pandas_compute_stats(df: pd.DataFrame) -> dict[str, str | int]:
    """Mirror the current stats computation with pandas."""
    stats: dict[str, str | int] = {"Total Chunks": len(df)}
    if "corpus_source" in df.columns:
        source_counts = df["corpus_source"].value_counts()
        for source, count in source_counts.items():
            stats[f"Source: {source}"] = int(count)
    if "embeddings" in df.columns:
        has_embed = df["embeddings"].apply(lambda value: value is not None and len(value) > 0).sum()
        stats["Chunks with Embeddings"] = int(has_embed)
        sample = df["embeddings"].dropna().iloc[0] if has_embed > 0 else None
        if sample is not None and hasattr(sample, "__len__"):
            stats["Embedding Dimension"] = len(sample)
    if "te_reo_terms" in df.columns:
        stats["Chunks with Te Reo"] = int(
            df["te_reo_terms"].apply(lambda value: isinstance(value, list) and len(value) > 0).sum()
        )
    if "nz_act_citations" in df.columns:
        stats["Chunks with Citations"] = int(
            df["nz_act_citations"].apply(lambda value: isinstance(value, list) and len(value) > 0).sum()
        )
    if "raw_text" in df.columns:
        stats["Total Words"] = int(df["raw_text"].str.split().str.len().sum())
    return stats


def _time_call(func: Callable[[], Any], iterations: int) -> dict[str, float | list[float]]:
    """Time a callable repeatedly and return millisecond summaries."""
    timings_ms: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        timings_ms.append((time.perf_counter() - start) * 1000)
    return {
        "mean_ms": fmean(timings_ms),
        "runs_ms": timings_ms,
    }


def _winner(pandas_mean_ms: float, polars_mean_ms: float) -> str:
    """Return the faster engine label."""
    return "polars" if polars_mean_ms <= pandas_mean_ms else "pandas"


def build_evidence(iterations: int = 10) -> dict[str, Any]:
    """Build deterministic benchmark evidence for the track."""
    frame = _sample_frame()

    with tempfile.TemporaryDirectory(prefix="track59_polars_") as tmpdir:
        parquet_path = Path(tmpdir) / "track59_sample.parquet"
        frame.to_parquet(parquet_path)

        pandas_load = _time_call(lambda: _pandas_load_parquet(parquet_path), iterations)
        polars_load = _time_call(lambda: load_parquet_polars(parquet_path), iterations)

        pandas_search = _time_call(lambda: _pandas_search_chunks("Education", frame, 10), iterations)
        polars_frame = pl.from_pandas(frame, include_index=False)
        polars_search = _time_call(
            lambda: search_chunks_polars("Education", polars_frame, 10),
            iterations,
        )

        pandas_stats = _time_call(lambda: _pandas_compute_stats(frame), iterations)
        polars_stats = _time_call(
            lambda: compute_stats_polars(polars_frame),
            iterations,
        )

    paths = [
        {
            "path": "load_parquet",
            "baseline": "pandas.read_parquet",
            "candidate": "polars.read_parquet",
            "baseline_mean_ms": pandas_load["mean_ms"],
            "candidate_mean_ms": polars_load["mean_ms"],
            "winner": _winner(pandas_load["mean_ms"], polars_load["mean_ms"]),
        },
        {
            "path": "search_chunks",
            "baseline": "pandas substring search",
            "candidate": "polars substring search",
            "baseline_mean_ms": pandas_search["mean_ms"],
            "candidate_mean_ms": polars_search["mean_ms"],
            "winner": _winner(pandas_search["mean_ms"], polars_search["mean_ms"]),
        },
        {
            "path": "compute_stats",
            "baseline": "pandas aggregations",
            "candidate": "polars aggregations",
            "baseline_mean_ms": pandas_stats["mean_ms"],
            "candidate_mean_ms": polars_stats["mean_ms"],
            "winner": _winner(pandas_stats["mean_ms"], polars_stats["mean_ms"]),
        },
    ]

    return {
        "track": TRACK_ID,
        "iterations": iterations,
        "sample_rows": len(frame),
        "ranked_hot_paths": [entry["path"] for entry in paths],
        "paths": paths,
        "policy": {
            "polars_only": ["src/nlp_policy_nz/storage/polars_pipeline.py"],
            "hybrid": ["spaces/app.py"],
            "pandas_boundary": [
                "Gradio dataframes",
                "public wrapper return values",
            ],
        },
        "recommendation": (
            "Adopt Polars for load_parquet and search_chunks, but keep compute_stats on pandas "
            "until a later optimisation closes the gap."
        ),
    }


def write_evidence(output: Path, iterations: int = 10) -> Path:
    """Write the benchmark evidence JSON to disk."""
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = build_evidence(iterations=iterations)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return output


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of timing runs per benchmark path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Where to write the benchmark evidence JSON.",
    )
    return parser


def main() -> int:
    """Run the benchmark and emit evidence JSON."""
    args = _build_parser().parse_args()
    write_evidence(args.output, iterations=args.iterations)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
