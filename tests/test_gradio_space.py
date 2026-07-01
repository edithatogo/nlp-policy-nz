"""Tests for Gradio Visualization Space (Track 8, Phase 2).

Tests the data transformation logic for each tab independently of Gradio
runtime: search, citations, Te Reo, and stats.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objects as go
import pytest

from spaces.app import (
    build_citation_network,
    build_corpus_statistics_chart,
    build_fixture_mode_notice,
    build_graph_vector_projection,
    build_ontology_coverage_table,
    build_publication_claims_table,
    build_tereo_chart,
    compute_stats,
    load_explorer_artifacts,
    load_parquet,
    search_chunks,
    summarize_explorer_artifacts,
)

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Return a small sample DataFrame mimicking pipeline output."""
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
    """Write sample_df to a temporary Parquet file."""
    path = tmp_path / "sample.parquet"
    sample_df.to_parquet(path)
    return path


# ---------------------------------------------------------------------------
# load_parquet tests
# ---------------------------------------------------------------------------


class TestLoadParquet:
    """Tests for :func:`load_parquet`."""

    def test_loads_file(self, sample_parquet: Path) -> None:
        """Verify a Parquet file loads into a DataFrame."""
        df = load_parquet(str(sample_parquet))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_none_path(self) -> None:
        """Verify None is returned for None input."""
        assert load_parquet(None) is None

    def test_missing_file(self) -> None:
        """Verify None is returned for a non-existent file."""
        assert load_parquet("/nonexistent/file.parquet") is None


# ---------------------------------------------------------------------------
# search_chunks tests
# ---------------------------------------------------------------------------


class TestSearchChunks:
    """Tests for :func:`search_chunks`."""

    def test_finds_match(self, sample_df: pd.DataFrame) -> None:
        """Verify a matching query returns results."""
        result = search_chunks("Climate Change", sample_df, 10)
        assert len(result) >= 1
        assert "Climate Change" in result.iloc[0]["raw_text"]

    def test_case_insensitive(self, sample_df: pd.DataFrame) -> None:
        """Verify search is case-insensitive."""
        result = search_chunks("education", sample_df, 10)
        assert len(result) >= 1

    def test_no_match(self, sample_df: pd.DataFrame) -> None:
        """Verify empty DataFrame for non-matching query."""
        result = search_chunks("zzzznonexistent", sample_df, 10)
        assert len(result) == 0

    def test_empty_query(self, sample_df: pd.DataFrame) -> None:
        """Verify empty DataFrame for empty query."""
        result = search_chunks("", sample_df, 10)
        assert len(result) == 0

    def test_none_df(self) -> None:
        """Verify empty DataFrame when df is None."""
        result = search_chunks("test", None, 10)
        assert len(result) == 0

    def test_top_k_limit(self, sample_df: pd.DataFrame) -> None:
        """Verify top_k limits the number of results."""
        result = search_chunks("Act", sample_df, 1)
        assert len(result) <= 1


# ---------------------------------------------------------------------------
# build_citation_network tests
# ---------------------------------------------------------------------------


class TestCitationNetwork:
    """Tests for :func:`build_citation_network`."""

    def test_returns_figure(self, sample_df: pd.DataFrame) -> None:
        """Verify a Plotly Figure is returned when citations exist."""
        fig = build_citation_network(sample_df)
        assert isinstance(fig, go.Figure)

    def test_none_df(self) -> None:
        """Verify a string message when df is None."""
        result = build_citation_network(None)
        assert isinstance(result, str)

    def test_no_citations_column(self) -> None:
        """Verify a string message when column is missing."""
        df = pd.DataFrame({"raw_text": ["hello"]})
        result = build_citation_network(df)
        assert isinstance(result, str)
        assert "No citation" in result

    def test_empty_citations(self) -> None:
        """Verify a string message when no citations are found."""
        df = pd.DataFrame({"nz_act_citations": [[], []]})
        result = build_citation_network(df)
        assert isinstance(result, str)
        assert "No citations" in result


# ---------------------------------------------------------------------------
# build_tereo_chart tests
# ---------------------------------------------------------------------------


class TestTereoChart:
    """Tests for :func:`build_tereo_chart`."""

    def test_returns_figure(self, sample_df: pd.DataFrame) -> None:
        """Verify a Plotly Figure is returned when Te Reo terms exist."""
        fig = build_tereo_chart(sample_df)
        assert isinstance(fig, go.Figure)

    def test_none_df(self) -> None:
        """Verify a string message when df is None."""
        result = build_tereo_chart(None)
        assert isinstance(result, str)

    def test_no_column(self) -> None:
        """Verify a string message when column is missing."""
        df = pd.DataFrame({"raw_text": ["hello"]})
        result = build_tereo_chart(df)
        assert isinstance(result, str)
        assert "No te_reo" in result

    def test_empty_terms(self) -> None:
        """Verify a string message when no terms are found."""
        df = pd.DataFrame({"te_reo_terms": [[], []]})
        result = build_tereo_chart(df)
        assert isinstance(result, str)
        assert "No Te Reo" in result


# ---------------------------------------------------------------------------
# compute_stats tests
# ---------------------------------------------------------------------------


class TestComputeStats:
    """Tests for :func:`compute_stats`."""

    def test_returns_dict(self, sample_df: pd.DataFrame) -> None:
        """Verify stats are returned as a dictionary."""
        stats = compute_stats(sample_df)
        assert isinstance(stats, dict)
        assert stats["Total Chunks"] == 3

    def test_source_breakdown(self, sample_df: pd.DataFrame) -> None:
        """Verify per-source counts are included."""
        stats = compute_stats(sample_df)
        assert "Source: legislation" in stats
        assert stats["Source: legislation"] == 2
        assert stats["Source: hansard"] == 1

    def test_embedding_info(self, sample_df: pd.DataFrame) -> None:
        """Verify embedding stats are computed."""
        stats = compute_stats(sample_df)
        assert "Chunks with Embeddings" in stats
        assert stats["Chunks with Embeddings"] == 2
        assert stats["Embedding Dimension"] == 3

    def test_tereo_info(self, sample_df: pd.DataFrame) -> None:
        """Verify Te Reo stats are computed."""
        stats = compute_stats(sample_df)
        assert "Chunks with Te Reo" in stats
        assert stats["Chunks with Te Reo"] == 1

    def test_citation_info(self, sample_df: pd.DataFrame) -> None:
        """Verify citation stats are computed."""
        stats = compute_stats(sample_df)
        assert "Chunks with Citations" in stats
        assert stats["Chunks with Citations"] == 2

    def test_total_words(self, sample_df: pd.DataFrame) -> None:
        """Verify total word count is computed."""
        stats = compute_stats(sample_df)
        assert "Total Words" in stats
        total_words = stats["Total Words"]
        assert isinstance(total_words, int)
        assert total_words > 0

    def test_none_df(self) -> None:
        """Verify fallback status when df is None."""
        stats = compute_stats(None)
        assert "Status" in stats


# ---------------------------------------------------------------------------
# Track 36 explorer artifact tests
# ---------------------------------------------------------------------------


class TestTrack36ExplorerArtifacts:
    """Tests for fixture-backed Hugging Face exploration pages."""

    def test_loads_checked_in_explorer_artifacts(self) -> None:
        """Verify Track 32-35 artifacts are loaded for fixture-mode pages."""
        artifacts = load_explorer_artifacts()

        assert artifacts["mode"] == "fixture"
        assert "corpus_statistics" in artifacts
        assert "ontology_coverage" in artifacts
        assert "graph_vector" in artifacts
        assert "analysis_artifacts" in artifacts
        assert "publication_protocol" in artifacts

    def test_fixture_notice_declares_full_corpus_boundary(self) -> None:
        """Verify the Space labels fixture-only evidence and missing full data."""
        notice = build_fixture_mode_notice()

        assert "Fixture mode" in notice
        assert "Requires full corpus" in notice
        assert "LanceDB" in notice

    def test_summary_surfaces_blockers_and_page_names(self) -> None:
        """Verify the overview summary is bounded and page-oriented."""
        summary = summarize_explorer_artifacts(load_explorer_artifacts())

        assert summary["mode"] == "fixture"
        assert summary["space_pages"] == [
            "Overview",
            "Corpus Statistics",
            "Ontology Coverage",
            "Graph and Vectors",
            "Artifacts",
            "Publication Protocol",
            "Dataset Browser",
        ]
        assert summary["known_blockers"] >= 1

    def test_builds_static_page_tables_and_figures(self) -> None:
        """Verify static exploration pages have renderable data."""
        artifacts = load_explorer_artifacts()

        ontology_table = build_ontology_coverage_table(artifacts)
        claims_table = build_publication_claims_table(artifacts)
        corpus_chart = build_corpus_statistics_chart(artifacts)
        vector_projection = build_graph_vector_projection(artifacts)

        assert not ontology_table.empty
        assert {"track", "metric", "value"}.issubset(ontology_table.columns)
        assert not claims_table.empty
        assert {"claim_id", "claim_status", "claim"}.issubset(claims_table.columns)
        assert isinstance(corpus_chart, go.Figure)
        assert isinstance(vector_projection, go.Figure)
