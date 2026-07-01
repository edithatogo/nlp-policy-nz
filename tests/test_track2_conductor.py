"""Track 2 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK2 = Path("conductor/tracks/archive/track2_external_repos_20260609")


def test_track2_conductor_registry_and_metadata_are_complete() -> None:
    """Track 2 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK2.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK2.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK2.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 2: Configure External Integrations & Data Sovereignty Registry (archived)" in registry
    assert str(TRACK2).replace("\\", "/") in registry
    assert metadata["track_id"] == "track2_external_repos_20260609"
    assert metadata["status"] == "archived"
    assert "Track 2 External Integrations & Data Sovereignty Registry" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK2.joinpath(required_file).is_file()


def test_track2_evidence_links_integration_surfaces() -> None:
    """Track 2 evidence records the integration modules and external gates."""
    evidence = TRACK2.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/integrations/huggingface.py"),
        Path("src/nlp_policy_nz/integrations/zenodo.py"),
        Path("src/nlp_policy_nz/integrations/data_registry.py"),
        Path("tests/integration/test_integrations_zenodo.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "Hugging Face" in evidence
    assert "Zenodo" in evidence
    assert "data sovereignty" in evidence.lower()
    assert "External gates" in evidence
