"""Track 10 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK10 = Path("conductor/tracks/archive/track10_deontic_modality_20260613")


def test_track10_conductor_registry_and_metadata_are_complete() -> None:
    """Track 10 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK10.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK10.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK10.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 10: Extract Deontic Modality & Legal Effect (archived)" in registry
    assert str(TRACK10).replace("\\", "/") in registry
    assert metadata["track_id"] == "track10_deontic_modality_20260613"
    assert metadata["status"] == "archived"
    assert "Track 10: Deontic Modality" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK10.joinpath(required_file).is_file()


def test_track10_evidence_links_legal_layer_surfaces() -> None:
    """Track 10 evidence records modality, legal effect, pipeline, and storage surfaces."""
    evidence = TRACK10.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/legal/modality.py"),
        Path("src/nlp_policy_nz/legal/effects.py"),
        Path("src/nlp_policy_nz/pipeline_api.py"),
        Path("src/nlp_policy_nz/storage/serialization.py"),
        Path("tests/test_modality.py"),
        Path("tests/test_legal_effects.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "DeonticModalityDetector" in evidence
    assert "classify_legal_effect" in evidence
    assert "External gates" in evidence
