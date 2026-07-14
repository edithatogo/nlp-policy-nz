"""Tests for Track 59 Polars-native corpus pipeline substitutions."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import polars as pl
import pytest

from nlp_policy_nz.storage.polars_pipeline import (
    compute_stats_polars,
    load_parquet_polars,
    search_chunks_polars,
)
from scripts.track59_polars_native_pipeline import build_evidence
from spaces.app import compute_stats, load_parquet, search_chunks


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Return a representative corpus browser fixture."""
    return pd.DataFrame(
        {
            "doc_id": ["leg-001", "leg-002", "han-001"],
            "corpus_source": ["legislation", "legislation", "hansard"],
            "raw_text": [
                "This Act amends the Climate Change Response Act 2002.",
                "Section 5 of the Education Act applies here.",
                "The member spoke about Treaty of Waitangi principles.",
            ],
            "cleaned_tokens": [
                ["This", "Act", "amends"],
                ["Section", "5", "of", "the", "Education", "Act"],
                ["The", "member", "spoke"],
            ],
            "nz_act_citations": [
                ["Climate Change Response Act 2002"],
                ["Education Act", "Education Act"],
                [],
            ],
            "te_reo_terms": [
                [],
                [],
                ["Treaty", "Waitangi", "Treaty"],
            ],
            "embeddings": [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
                None,
            ],
        }
    )


@pytest.fixture
def sample_parquet(tmp_path: Path, sample_df: pd.DataFrame) -> Path:
    """Write the sample frame to a Parquet file."""
    path = tmp_path / "sample.parquet"
    sample_df.to_parquet(path)
    return path


def test_load_parquet_polars_reads_rows(sample_parquet: Path) -> None:
    """The Polars loader should read the same row count as pandas."""
    df = load_parquet_polars(sample_parquet)

    assert isinstance(df, pl.DataFrame)
    assert df.height == 3
    assert df.columns[0] == "doc_id"


def test_load_parquet_wrapper_keeps_pandas_boundary(sample_parquet: Path) -> None:
    """The UI wrapper should continue returning pandas DataFrames."""
    df = load_parquet(str(sample_parquet))

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3


def test_search_chunks_polars_matches_wrapper(sample_df: pd.DataFrame) -> None:
    """The Polars search should match the public pandas wrapper."""
    polars_df = pl.from_pandas(sample_df, include_index=False)

    core = search_chunks_polars("Education", polars_df, 10)
    wrapper = search_chunks("Education", sample_df, 10)

    assert core.to_pandas().equals(wrapper)


def test_search_chunks_polars_handles_missing_inputs() -> None:
    """The Polars search should return an empty frame for missing inputs."""
    assert search_chunks_polars("", None, 10).is_empty()
    assert search_chunks_polars("test", pl.DataFrame(), 10).is_empty()


def test_compute_stats_polars_matches_wrapper(sample_df: pd.DataFrame) -> None:
    """The Polars stats helper should match the public wrapper."""
    polars_df = pl.from_pandas(sample_df, include_index=False)

    core = compute_stats_polars(polars_df)
    wrapper = compute_stats(sample_df)

    assert core == wrapper


def test_compute_stats_polars_handles_none() -> None:
    """The Polars stats helper should preserve the no-data status."""
    assert compute_stats_polars(None) == {"Status": "No dataset loaded"}


def test_track59_benchmark_payload_can_be_serialised(sample_df: pd.DataFrame) -> None:
    """The benchmark data shape should remain JSON serialisable."""
    payload = {
        "track": 59,
        "frame_rows": len(sample_df),
        "comparison": {
            "search": search_chunks("Education", sample_df, 10).to_dict(orient="records"),
            "stats": compute_stats(sample_df),
        },
    }

    encoded = json.dumps(payload, sort_keys=True)
    assert '"track": 59' in encoded


def test_track59_benchmark_evidence_has_ranked_paths() -> None:
    """The benchmark harness should emit a ranked path summary."""
    evidence = build_evidence(iterations=1)

    assert evidence["track"] == "track59_polars_native_pipeline_20260701"
    assert evidence["ranked_hot_paths"] == [
        "load_parquet",
        "search_chunks",
        "compute_stats",
    ]
    assert len(evidence["paths"]) == 3
