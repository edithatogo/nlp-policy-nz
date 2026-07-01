"""Track 8 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK8 = Path("conductor/tracks/archive/track8_huggingface_20260612")


def test_track8_conductor_registry_and_metadata_are_complete() -> None:
    """Track 8 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK8.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK8.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK8.joinpath("spec.md").read_text(encoding="utf-8")

    assert (
        "## [x] Track 8: Deploy Hugging Face Datasets & Interactive Visualization Spaces (archived)"
        in registry
    )
    assert str(TRACK8).replace("\\", "/") in registry
    assert metadata["track_id"] == "track8_huggingface_20260612"
    assert metadata["status"] == "archived"
    assert "Track 8: Deploy Hugging Face Datasets" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK8.joinpath(required_file).is_file()


def test_track8_evidence_links_huggingface_surfaces() -> None:
    """Track 8 evidence records upload, dataset-card, Space, and CLI validation."""
    evidence = TRACK8.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/integrations/hf_uploader.py"),
        Path("src/nlp_policy_nz/integrations/dataset_card.py"),
        Path("spaces/app.py"),
        Path("tests/test_hf_upload.py"),
        Path("tests/test_dataset_card.py"),
        Path("tests/test_gradio_space.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "upload-dataset" in evidence
    assert "deploy-space" in evidence
    assert "External gates" in evidence
