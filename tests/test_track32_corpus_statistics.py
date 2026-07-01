"""Tests for Track 32 whole-corpus descriptive statistics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from nlp_policy_nz.analysis.corpus_statistics import (
    CORPUS_STATISTICS_BLOCKERS_FILENAME,
    CORPUS_STATISTICS_ENTITY_TYPES_FILENAME,
    CORPUS_STATISTICS_MANIFEST_FILENAME,
    CORPUS_STATISTICS_MARKDOWN_FILENAME,
    CORPUS_STATISTICS_ONTOLOGY_FILENAME,
    CORPUS_STATISTICS_PER_CORPUS_FILENAME,
    CORPUS_STATISTICS_PER_YEAR_FILENAME,
    build_corpus_statistics,
    build_fixture_records,
    write_corpus_statistics_artifacts,
)
from nlp_policy_nz.cli.main import main
from nlp_policy_nz.storage import PipelineRecord, load_from_parquet, serialize_to_parquet


def _records() -> tuple[PipelineRecord, ...]:
    return (
        PipelineRecord(
            doc_id="legislation-2024-001",
            corpus_source="legislation",
            raw_text="A person must file a return by 1 July 2024. Maori terms include tikanga.",
            cleaned_tokens=["A", "person", "must", "file", "a", "return", "by", "1", "July", "2024"],
            nz_act_citations=["Example Act 2024"],
            te_reo_terms=["tikanga"],
            embeddings=[0.1, 0.2, 0.3],
            deontic_modality=(
                {"label": "obligation", "text": "must", "year": "2024"},
            ),
            temporal_expressions=(
                {"label": "date", "value": "2024-07-01", "text": "1 July 2024"},
            ),
            resolved_entities=(
                {"label": "Ministry", "type": "ORG", "qid": "Q1"},
                {"label": "Auckland", "type": "GPE", "qid": "Q2"},
            ),
            legal_effect="obligation",
        ),
        PipelineRecord(
            doc_id="hansard-2025-001",
            corpus_source="hansard",
            raw_text="The House debated health policy in 2025. The member may respond.",
            cleaned_tokens=["The", "House", "debated", "health", "policy", "in", "2025"],
            nz_act_citations=[],
            te_reo_terms=[],
            embeddings=None,
            deontic_modality=(
                {"label": "permission", "text": "may", "year": "2025"},
            ),
            temporal_expressions=(
                {"label": "year", "value": "2025", "text": "2025"},
            ),
            resolved_entities=(
                {"label": "House", "entity_type": "ORG"},
            ),
            voting_record={"motion": "Health vote", "outcome": "agreed"},
            stance="pro",
        ),
    )


def test_corpus_statistics_summarises_pipeline_records_and_years() -> None:
    """Track 32 should summarize corpus, temporal, entity, and vector metrics."""
    bundle = build_corpus_statistics(records=_records())

    assert bundle.manifest["summary"]["record_count"] == 2
    assert bundle.per_corpus[0]["corpus_source"] == "hansard"
    assert bundle.per_corpus[1]["corpus_source"] == "legislation"
    assert bundle.per_year == (
        {
            "year": 2024,
            "record_count": 1,
            "corpus_sources": ["legislation"],
            "token_count": 10,
            "citation_count": 1,
            "deontic_count": 1,
            "temporal_expression_count": 1,
        },
        {
            "year": 2025,
            "record_count": 1,
            "corpus_sources": ["hansard"],
            "token_count": 7,
            "citation_count": 0,
            "deontic_count": 1,
            "temporal_expression_count": 1,
        },
    )
    assert {row["entity_type"]: row["entity_count"] for row in bundle.entity_types} == {
        "GPE": 1,
        "ORG": 2,
    }
    assert bundle.manifest["summary"]["embedding_record_count"] == 1


def test_corpus_statistics_includes_ontology_coverage_and_blockers() -> None:
    """Track 32 should aggregate ontology artifacts and record data blockers."""
    bundle = build_corpus_statistics(records=_records())
    ontology = bundle.ontology_coverage

    assert ontology["track25"]["row_count"] > 0
    assert ontology["track29"]["mapping_count"] >= 10
    assert ontology["track30"]["candidate_count"] >= 4
    assert ontology["track31"]["concept_count"] >= 10
    assert any(blocker["blocker_type"] == "full_corpus_unavailable" for blocker in bundle.blockers)
    assert any(blocker["corpus"] == "case_law" for blocker in bundle.blockers)


def test_corpus_statistics_artifact_writer_round_trips(tmp_path: Path) -> None:
    """Writer should emit JSON, CSV, and Markdown artifacts deterministically."""
    written = write_corpus_statistics_artifacts(tmp_path, records=_records())

    assert set(written) == {
        CORPUS_STATISTICS_MANIFEST_FILENAME,
        CORPUS_STATISTICS_PER_CORPUS_FILENAME,
        CORPUS_STATISTICS_PER_YEAR_FILENAME,
        CORPUS_STATISTICS_ENTITY_TYPES_FILENAME,
        CORPUS_STATISTICS_ONTOLOGY_FILENAME,
        CORPUS_STATISTICS_BLOCKERS_FILENAME,
        CORPUS_STATISTICS_MARKDOWN_FILENAME,
    }
    manifest = json.loads(written[CORPUS_STATISTICS_MANIFEST_FILENAME].read_text(encoding="utf-8"))
    per_corpus_rows = list(
        csv.DictReader(written[CORPUS_STATISTICS_PER_CORPUS_FILENAME].open(encoding="utf-8"))
    )
    markdown = written[CORPUS_STATISTICS_MARKDOWN_FILENAME].read_text(encoding="utf-8")

    assert manifest["track_id"] == "track32_corpus_descriptive_statistics_20260625"
    assert manifest["summary"]["record_count"] == 2
    assert {row["corpus_source"] for row in per_corpus_rows} == {"hansard", "legislation"}
    assert "Whole-Corpus Descriptive Statistics" in markdown


def test_checked_in_corpus_statistics_artifacts_match_writer(tmp_path: Path) -> None:
    """Checked-in Track 32 artifacts should stay in sync with the writer."""
    written = write_corpus_statistics_artifacts(tmp_path, markdown_path=tmp_path / "summary.md")
    checked_in_dir = Path("data/statistics")
    checked_in_docs = Path("docs/corpus_statistics.md")

    for filename in (
        CORPUS_STATISTICS_MANIFEST_FILENAME,
        CORPUS_STATISTICS_ONTOLOGY_FILENAME,
        CORPUS_STATISTICS_BLOCKERS_FILENAME,
    ):
        checked_in = json.loads(checked_in_dir.joinpath(filename).read_text(encoding="utf-8"))
        generated = json.loads(written[filename].read_text(encoding="utf-8"))
        assert checked_in == generated

    for filename in (
        CORPUS_STATISTICS_PER_CORPUS_FILENAME,
        CORPUS_STATISTICS_PER_YEAR_FILENAME,
        CORPUS_STATISTICS_ENTITY_TYPES_FILENAME,
    ):
        assert checked_in_dir.joinpath(filename).read_text(encoding="utf-8") == (
            written[filename].read_text(encoding="utf-8")
        )

    assert checked_in_docs.read_text(encoding="utf-8") == (
        written[CORPUS_STATISTICS_MARKDOWN_FILENAME].read_text(encoding="utf-8")
    )


def test_corpus_statistics_loads_pipeline_record_parquet(tmp_path: Path) -> None:
    """Track 32 should accept PipelineRecord Parquet inputs."""
    parquet_path = serialize_to_parquet(_records(), tmp_path / "records.parquet")
    loaded = tuple(load_from_parquet(parquet_path))

    assert [record.doc_id for record in loaded] == ["legislation-2024-001", "hansard-2025-001"]
    assert build_corpus_statistics(records=loaded).manifest["summary"]["record_count"] == 2


def test_corpus_stats_cli_writes_artifacts_from_parquet(tmp_path: Path) -> None:
    """The corpus-stats CLI should dispatch to the Track 32 writer."""
    parquet_path = serialize_to_parquet(_records(), tmp_path / "records.parquet")
    output_dir = tmp_path / "stats"

    rc = main(["corpus-stats", "--parquet", str(parquet_path), "--output-dir", str(output_dir)])

    assert rc == 0
    assert output_dir.joinpath(CORPUS_STATISTICS_MANIFEST_FILENAME).is_file()
    assert output_dir.joinpath(CORPUS_STATISTICS_PER_YEAR_FILENAME).is_file()


def test_fixture_records_are_available_when_full_corpus_is_absent() -> None:
    """Fixture records provide a deterministic repo-side fallback."""
    fixtures = build_fixture_records()

    assert {record.corpus_source for record in fixtures} >= {"legislation", "hansard"}
    assert build_corpus_statistics(records=fixtures).blockers
