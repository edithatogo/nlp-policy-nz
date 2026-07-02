"""Polars-native helpers for the corpus browser hot paths.

These functions provide a small Polars core for the tabular surfaces that back
the Gradio dataset browser while keeping the public UI boundary stable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import polars as pl

__all__ = [
    "compute_stats_polars",
    "load_parquet_polars",
    "search_chunks_polars",
]


def load_parquet_polars(file_path: str | Path | None) -> pl.DataFrame | None:
    """Load a Parquet file into a Polars DataFrame."""
    if file_path is None:
        return None

    path = Path(file_path)
    if not path.is_file():
        return None

    return pl.read_parquet(path)


def _non_empty_list_expr(column: str) -> pl.Expr:
    """Return a boolean expression that marks non-empty list rows."""
    return pl.col(column).is_not_null() & (pl.col(column).list.len().fill_null(0) > 0)


def _count_non_empty_lists(df: pl.DataFrame, column: str) -> int:
    """Count rows where the named list column contains at least one value."""
    if column not in df.columns:
        return 0
    total = df.select(_non_empty_list_expr(column).cast(pl.Int64).sum()).item()
    return int(total or 0)


def _first_non_empty_list(df: pl.DataFrame, column: str) -> list[Any] | None:
    """Return the first non-empty list from a Polars column, if present."""
    if column not in df.columns:
        return None

    series = df.filter(_non_empty_list_expr(column)).get_column(column)
    if series.is_empty():
        return None

    first_value = series.to_list()[0]
    if isinstance(first_value, list):
        return first_value
    return None


def search_chunks_polars(
    query: str,
    df: pl.DataFrame | None,
    top_k: int,
) -> pl.DataFrame:
    """Search document chunks by case-insensitive substring matching."""
    if df is None or not query.strip():
        return pl.DataFrame(schema={"doc_id": pl.Utf8, "corpus_source": pl.Utf8, "raw_text": pl.Utf8, "relevance": pl.Float64})

    if "raw_text" not in df.columns:
        return pl.DataFrame(schema={"doc_id": pl.Utf8, "corpus_source": pl.Utf8, "raw_text": pl.Utf8, "relevance": pl.Float64})

    query_lower = query.casefold()
    available_columns = [
        column for column in ("doc_id", "corpus_source", "raw_text") if column in df.columns
    ]
    frame = df.select(available_columns)

    filtered = frame.filter(
        pl.col("raw_text")
        .cast(pl.Utf8)
        .fill_null("")
        .str.to_lowercase()
        .str.contains(query_lower, literal=True)
    )
    if filtered.is_empty():
        return filtered.with_columns(pl.lit(None, dtype=pl.Float64).alias("relevance")).select(
            ["doc_id", "corpus_source", "raw_text", "relevance"]
        )

    result = filtered.with_columns(
        relevance=(
            pl.col("raw_text")
            .cast(pl.Utf8)
            .fill_null("")
            .str.to_lowercase()
            .str.count_matches(query_lower, literal=True)
            / pl.col("raw_text")
            .cast(pl.Utf8)
            .fill_null("")
            .map_elements(lambda text: len(str(text).split()), return_dtype=pl.Int64)
        )
    ).select(["doc_id", "corpus_source", "raw_text", "relevance"])

    return result.sort("relevance", descending=True).head(top_k)


def compute_stats_polars(df: pl.DataFrame | None) -> dict[str, str | int]:
    """Compute corpus-level statistics using Polars expressions."""
    if df is None:
        return {"Status": "No dataset loaded"}

    stats: dict[str, str | int] = {"Total Chunks": df.height}

    if "corpus_source" in df.columns:
        source_counts = (
            df.group_by("corpus_source")
            .len()
            .sort("corpus_source")
        )
        for row in source_counts.iter_rows(named=True):
            source = str(row["corpus_source"])
            stats[f"Source: {source}"] = int(row["len"])

    if "embeddings" in df.columns:
        has_embed = _count_non_empty_lists(df, "embeddings")
        stats["Chunks with Embeddings"] = has_embed
        sample = _first_non_empty_list(df, "embeddings")
        if sample is not None:
            stats["Embedding Dimension"] = len(sample)

    if "te_reo_terms" in df.columns:
        stats["Chunks with Te Reo"] = _count_non_empty_lists(df, "te_reo_terms")

    if "nz_act_citations" in df.columns:
        stats["Chunks with Citations"] = _count_non_empty_lists(df, "nz_act_citations")

    if "raw_text" in df.columns:
        total_words = (
            df.select(
                pl.col("raw_text")
                .cast(pl.Utf8)
                .fill_null("")
                .str.count_matches(r"\S+")
                .sum()
            )
            .item()
        )
        stats["Total Words"] = int(total_words or 0)

    return stats
