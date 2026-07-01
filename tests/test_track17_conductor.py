"""Conductor contract tests for Track 17."""

from __future__ import annotations

import json
from pathlib import Path

TRACK17 = Path("conductor/tracks/archive/track17_wikidata_integration_20260613")


def test_track17_conductor_registry_and_metadata_are_complete() -> None:
    """Track 17 remains discoverable as an archived Conductor track."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK17.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK17.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK17.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 17: Wikidata NZ Ontology Integration (archived)" in registry
    assert str(TRACK17).replace("\\", "/") in registry
    assert metadata["track_id"] == "track17_wikidata_integration_20260613"
    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK17.joinpath(required_file).is_file()


def test_track17_evidence_links_wikidata_surfaces() -> None:
    """Track 17 evidence records Wikidata, cache, RDF, CLI, and tests."""
    evidence = TRACK17.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("data/ontologies/nz_wikidata_map.ttl"),
        Path("data/ontologies/wikidata_federated_example.rq"),
        Path("src/nlp_policy_nz/kb/wikidata_kg.py"),
        Path("src/nlp_policy_nz/kb/sparql_cache.py"),
        Path("src/nlp_policy_nz/cli/main.py"),
        Path("tests/test_wikidata_kg.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert str(artifact).replace("\\", "/") in evidence

    assert "knowledge-graph" in evidence
    assert "external evaluation gate" in evidence


def test_track17_archive_index_links_required_review_artifacts() -> None:
    """The archive index exposes every Track 17 review artifact."""
    index = TRACK17.joinpath("index.md").read_text(encoding="utf-8")

    for file_name in ("spec.md", "plan.md", "metadata.json", "evidence.md"):
        assert file_name in index
