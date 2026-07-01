"""Conductor contract tests for Track 16."""

from __future__ import annotations

import json
from pathlib import Path

TRACK16 = Path("conductor/tracks/archive/track16_faaf_sioc_discourse_20260613")


def test_track16_conductor_registry_and_metadata_are_complete() -> None:
    """Track 16 remains discoverable as an archived Conductor track."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK16.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK16.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK16.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 16: FOAF & SIOC Ontologies for Parliamentary Discourse (archived)" in registry
    assert str(TRACK16).replace("\\", "/") in registry
    assert metadata["track_id"] == "track16_faaf_sioc_discourse_20260613"
    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK16.joinpath(required_file).is_file()


def test_track16_evidence_links_linked_data_surfaces() -> None:
    """Track 16 evidence records FOAF, SIOC, RDF, CLI, and tests."""
    evidence = TRACK16.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/linked_data/foaf.py"),
        Path("src/nlp_policy_nz/linked_data/sioc.py"),
        Path("src/nlp_policy_nz/linked_data/rdf.py"),
        Path("src/nlp_policy_nz/cli/main.py"),
        Path("tests/test_linked_data.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert str(artifact).replace("\\", "/") in evidence

    assert "export-rdf" in evidence
    assert "sparql" in evidence
    assert "external data gate" in evidence


def test_track16_archive_index_links_required_review_artifacts() -> None:
    """The archive index exposes every Track 16 review artifact."""
    index = TRACK16.joinpath("index.md").read_text(encoding="utf-8")

    for file_name in ("spec.md", "plan.md", "metadata.json", "evidence.md"):
        assert file_name in index
