"""Tests for Track 33 graph, vector, and network analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from nlp_policy_nz.analysis.graph_vector_network import (
    GRAPH_VECTOR_ALIGNMENT_FILENAME,
    GRAPH_VECTOR_BLOCKERS_FILENAME,
    GRAPH_VECTOR_GRAPH_METRICS_FILENAME,
    GRAPH_VECTOR_MANIFEST_FILENAME,
    GRAPH_VECTOR_MARKDOWN_FILENAME,
    GRAPH_VECTOR_MERMAID_FILENAME,
    GRAPH_VECTOR_VECTOR_METRICS_FILENAME,
    build_fixture_vector_records,
    build_graph_vector_network_analysis,
    write_graph_vector_network_artifacts,
)
from nlp_policy_nz.cli.main import main


def test_graph_vector_analysis_computes_graph_and_vector_metrics() -> None:
    """Track 33 should summarize graph topology and vector structure."""
    bundle = build_graph_vector_network_analysis()

    assert bundle.manifest["track_id"] == "track33_graph_vector_network_analysis_20260625"
    assert bundle.graph_metrics["summary"]["node_count"] >= 20
    assert bundle.graph_metrics["summary"]["edge_count"] >= 20
    assert bundle.graph_metrics["centrality"]["degree_top"]
    assert bundle.graph_metrics["communities"]["community_count"] >= 2
    assert bundle.vector_metrics["summary"]["vector_count"] >= 6
    assert bundle.vector_metrics["nearest_neighbors"]
    assert bundle.vector_metrics["clusters"]["cluster_count"] >= 2


def test_graph_vector_analysis_reports_alignment_and_blockers() -> None:
    """Track 33 should compare graph links with vector neighbours and record blockers."""
    bundle = build_graph_vector_network_analysis()

    assert bundle.alignment_rows
    assert any(row["aligned_in_top3"] for row in bundle.alignment_rows)
    assert any(blocker["blocker_type"] == "full_graph_unavailable" for blocker in bundle.blockers)
    assert any(blocker["blocker_type"] == "full_vector_index_unavailable" for blocker in bundle.blockers)


def test_graph_vector_artifact_writer_round_trips(tmp_path: Path) -> None:
    """Writer should emit deterministic JSON, CSV, Mermaid, and Markdown artifacts."""
    written = write_graph_vector_network_artifacts(tmp_path, markdown_path=tmp_path / "summary.md")

    assert set(written) == {
        GRAPH_VECTOR_MANIFEST_FILENAME,
        GRAPH_VECTOR_GRAPH_METRICS_FILENAME,
        GRAPH_VECTOR_VECTOR_METRICS_FILENAME,
        GRAPH_VECTOR_ALIGNMENT_FILENAME,
        GRAPH_VECTOR_BLOCKERS_FILENAME,
        GRAPH_VECTOR_MERMAID_FILENAME,
        GRAPH_VECTOR_MARKDOWN_FILENAME,
    }
    manifest = json.loads(written[GRAPH_VECTOR_MANIFEST_FILENAME].read_text(encoding="utf-8"))
    rows = list(csv.DictReader(written[GRAPH_VECTOR_ALIGNMENT_FILENAME].open(encoding="utf-8")))
    mermaid = written[GRAPH_VECTOR_MERMAID_FILENAME].read_text(encoding="utf-8")
    markdown = written[GRAPH_VECTOR_MARKDOWN_FILENAME].read_text(encoding="utf-8")

    assert manifest["summary"]["alignment_pair_count"] == len(rows)
    assert rows[0]["source_id"]
    assert mermaid.startswith("graph LR")
    assert "Graph, Vector, and Network Analysis" in markdown


def test_checked_in_graph_vector_artifacts_match_writer(tmp_path: Path) -> None:
    """Checked-in Track 33 artifacts should stay in sync with the writer."""
    written = write_graph_vector_network_artifacts(tmp_path, markdown_path=tmp_path / "summary.md")
    checked_in_dir = Path("data/analysis")
    checked_in_doc = Path("docs/graph_vector_network_analysis.md")

    for filename in (
        GRAPH_VECTOR_MANIFEST_FILENAME,
        GRAPH_VECTOR_GRAPH_METRICS_FILENAME,
        GRAPH_VECTOR_VECTOR_METRICS_FILENAME,
        GRAPH_VECTOR_BLOCKERS_FILENAME,
    ):
        checked_in = json.loads(checked_in_dir.joinpath(filename).read_text(encoding="utf-8"))
        generated = json.loads(written[filename].read_text(encoding="utf-8"))
        assert checked_in == generated

    for filename in (GRAPH_VECTOR_ALIGNMENT_FILENAME, GRAPH_VECTOR_MERMAID_FILENAME):
        assert checked_in_dir.joinpath(filename).read_text(encoding="utf-8") == (
            written[filename].read_text(encoding="utf-8")
        )
    assert checked_in_doc.read_text(encoding="utf-8") == (
        written[GRAPH_VECTOR_MARKDOWN_FILENAME].read_text(encoding="utf-8")
    )


def test_graph_vector_cli_writes_artifacts(tmp_path: Path) -> None:
    """The CLI should dispatch to the Track 33 artifact writer."""
    output_dir = tmp_path / "analysis"

    rc = main(["graph-vector-analysis", "--output-dir", str(output_dir)])

    assert rc == 0
    assert output_dir.joinpath(GRAPH_VECTOR_MANIFEST_FILENAME).is_file()
    assert output_dir.joinpath(GRAPH_VECTOR_ALIGNMENT_FILENAME).is_file()
    assert output_dir.joinpath(GRAPH_VECTOR_MARKDOWN_FILENAME).is_file()


def test_fixture_vector_records_are_deterministic() -> None:
    """Fixture vector records should provide stable repo-side evidence."""
    records = build_fixture_vector_records()

    assert [record.record_id for record in records] == sorted(
        record.record_id for record in records
    )
    assert all(len(record.vector) == 4 for record in records)
