"""Tests for Track 37 publication manuscript and review agents."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.publication.manuscript import (
    MANUSCRIPT_REVIEW_LOG_FILENAME,
    MANUSCRIPT_RUBRICS_FILENAME,
    build_manuscript_package,
    write_manuscript_package,
)


def test_track37_package_contains_manuscript_supplement_and_reviews() -> None:
    """Track 37 should create manuscript scaffolds and bounded review scores."""
    package = build_manuscript_package()

    assert package.manifest["track_id"] == "track37_publication_manuscript_review_20260625"
    assert package.manifest["summary"]["manuscript_document_count"] >= 4
    assert package.manifest["summary"]["reviewer_count"] >= 6
    assert package.manifest["summary"]["minimum_score"] > 95
    assert "arXiv" in package.requirements
    assert "## Methods" in package.documents["manuscript.md"]
    assert "## Figure gallery" in package.documents["supplement.md"]
    assert "## Comparative tooling and deployment choices" in package.documents["manuscript.md"]
    assert "## Data and code availability" in package.documents["manuscript.md"]
    assert "## Decision appendix" in package.documents["manuscript.md"]
    assert all(review["score"] > 95 for review in package.review_log["reviews"])


def test_track37_writer_emits_expected_files(tmp_path: Path) -> None:
    """The Track 37 writer should emit manuscript, supplement, and review artifacts."""
    written = write_manuscript_package(tmp_path)

    assert written["manuscript_manifest.json"].is_file()
    assert written[MANUSCRIPT_REVIEW_LOG_FILENAME].is_file()
    assert written[MANUSCRIPT_RUBRICS_FILENAME].is_file()
    assert tmp_path.joinpath("manuscript.md").is_file()
    assert tmp_path.joinpath("abstract.md").is_file()
    assert tmp_path.joinpath("supplement.md").is_file()
    assert tmp_path.joinpath("submission_requirements.md").is_file()
    assert tmp_path.joinpath("scripts", "manuscript", "main.tex").is_file()
    assert tmp_path.joinpath("scripts", "manuscript", "Makefile").is_file()

    review_log = json.loads(written[MANUSCRIPT_REVIEW_LOG_FILENAME].read_text(encoding="utf-8"))
    assert review_log["overall"]["score"] > 95


def test_checked_in_track37_artifacts_match_writer(tmp_path: Path) -> None:
    """Checked-in Track 37 artifacts should stay in sync with the writer."""
    written = write_manuscript_package(tmp_path)
    checked_in_dir = Path("artifacts") / "manuscript"

    for relative_path, generated_path in written.items():
        checked_in_path = checked_in_dir.joinpath(relative_path)
        assert checked_in_path.read_text(encoding="utf-8") == generated_path.read_text(
            encoding="utf-8"
        )


def test_root_manuscript_latex_scaffold_matches_generated_bundle() -> None:
    """The repo-level LaTeX scaffold should mirror the generated arXiv bundle."""
    for filename in ("main.tex", "macros.tex", "references.bib", "Makefile"):
        root_file = Path("scripts") / "manuscript" / filename
        generated_file = Path("artifacts") / "manuscript" / "scripts" / "manuscript" / filename

        assert root_file.is_file()
        assert root_file.read_text(encoding="utf-8") == generated_file.read_text(
            encoding="utf-8"
        )


def test_track37_cli_dispatches_writer(tmp_path: Path) -> None:
    """The CLI should dispatch to the Track 37 manuscript writer."""
    output_dir = tmp_path / "manuscript"

    rc = main(["generate-manuscript-package", "--output-dir", str(output_dir)])

    assert rc == 0
    assert output_dir.joinpath("manuscript.md").is_file()
    assert output_dir.joinpath(MANUSCRIPT_REVIEW_LOG_FILENAME).is_file()


def test_track37_workflow_is_offline_and_posts_pr_summary() -> None:
    """The manuscript review workflow should run offline and publish PR feedback."""
    workflow = Path(".github/workflows/manuscript-review.yml").read_text(encoding="utf-8")

    assert "generate-manuscript-package" in workflow
    assert "tests/test_track37_manuscript_review.py" in workflow
    assert "actions/github-script" in workflow
    assert "MANUSCRIPT_REVIEW_LOG" in workflow
