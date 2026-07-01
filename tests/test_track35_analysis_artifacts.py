"""Tests for Track 35 analysis artifact execution and figure production."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.analysis import (
    ANALYSIS_ARTIFACT_BLOCKERS_FILENAME,
    ANALYSIS_ARTIFACT_MANIFEST_FILENAME,
    ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME,
    build_analysis_artifact_bundle,
    write_analysis_artifacts,
)
from nlp_policy_nz.cli.main import main


def test_track35_bundle_lists_tables_figures_diagrams_and_blockers() -> None:
    """Track 35 should inventory publication tables, figures, diagrams, and blockers."""
    bundle = build_analysis_artifact_bundle()

    manifest = bundle.manifest
    available = {item["artifact_id"] for item in manifest["artifacts"]}
    blocked = {item["artifact_id"] for item in bundle.blockers}

    assert manifest["track_id"] == "track35_analysis_artifact_execution_20260625"
    assert manifest["summary"]["available_count"] >= 8
    assert manifest["summary"]["blocked_count"] >= 1
    assert "table-corpus-summary" in available
    assert "figure-temporal-trends" in available
    assert "diagram-pipeline-architecture" in available
    assert "full-corpus-embedding-umap" in blocked
    assert all(item["output_path"] for item in manifest["artifacts"])


def test_track35_writer_emits_expected_artifact_files(tmp_path: Path) -> None:
    """The Track 35 writer should emit manifest, tables, figures, diagrams, and checks."""
    written = write_analysis_artifacts(tmp_path)

    assert written[ANALYSIS_ARTIFACT_MANIFEST_FILENAME].is_file()
    assert written[ANALYSIS_ARTIFACT_BLOCKERS_FILENAME].is_file()
    assert written[ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME].is_file()
    assert tmp_path.joinpath("tables", "corpus_summary.csv").is_file()
    assert tmp_path.joinpath("tables", "corpus_summary.tex").is_file()
    assert tmp_path.joinpath("figures", "temporal_trends.svg").is_file()
    assert tmp_path.joinpath("figures", "network_overview.svg").is_file()
    assert tmp_path.joinpath("diagrams", "pipeline_architecture.mmd").is_file()

    manifest = json.loads(
        written[ANALYSIS_ARTIFACT_MANIFEST_FILENAME].read_text(encoding="utf-8")
    )
    assert manifest["summary"]["table_count"] >= 4
    assert manifest["summary"]["figure_count"] >= 4
    assert manifest["summary"]["diagram_count"] >= 3


def test_checked_in_track35_artifacts_match_writer(tmp_path: Path) -> None:
    """Checked-in Track 35 artifacts should stay in sync with the writer."""
    written = write_analysis_artifacts(tmp_path)
    checked_in_dir = Path("artifacts")

    for relative_path in (
        ANALYSIS_ARTIFACT_MANIFEST_FILENAME,
        ANALYSIS_ARTIFACT_BLOCKERS_FILENAME,
        ANALYSIS_ARTIFACT_VISUAL_CHECKLIST_FILENAME,
        "tables/corpus_summary.csv",
        "tables/corpus_summary.tex",
        "figures/temporal_trends.svg",
        "figures/network_overview.svg",
        "diagrams/pipeline_architecture.mmd",
        "diagrams/workflow_data_flow.mmd",
        "diagrams/track_dependency.mmd",
    ):
        assert checked_in_dir.joinpath(relative_path).read_text(encoding="utf-8") == (
            written[relative_path].read_text(encoding="utf-8")
        )


def test_track35_cli_dispatches_writer(tmp_path: Path) -> None:
    """The CLI should dispatch to the Track 35 artifact writer."""
    output_dir = tmp_path / "artifacts"

    rc = main(["generate-analysis-artifacts", "--output-dir", str(output_dir)])

    assert rc == 0
    assert output_dir.joinpath(ANALYSIS_ARTIFACT_MANIFEST_FILENAME).is_file()
    assert output_dir.joinpath("figures", "embedding_projection.svg").is_file()
