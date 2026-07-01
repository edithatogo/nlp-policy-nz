"""Track 5 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK5 = Path("conductor/tracks/archive/track5_semantic_layer_20260609")


def test_track5_conductor_registry_and_metadata_are_complete() -> None:
    """Track 5 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK5.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK5.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK5.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 5: Integrate Semantic Layer & Quantized Embeddings (archived)" in registry
    assert str(TRACK5).replace("\\", "/") in registry
    assert metadata["track_id"] == "track5_semantic_layer_20260609"
    assert metadata["status"] == "archived"
    assert "Track 5 Semantic Layer & Quantized Embeddings" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK5.joinpath(required_file).is_file()


def test_track5_evidence_links_semantic_surfaces() -> None:
    """Track 5 evidence records the semantic modules and validation surface."""
    evidence = TRACK5.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/semantic/model_loader.py"),
        Path("src/nlp_policy_nz/semantic/embeddings.py"),
        Path("tests/test_semantic.py"),
        Path("tests/test_embeddings.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "Hugging Face" in evidence
    assert "quantization" in evidence
    assert "EmbeddingGenerator" in evidence
    assert "External gates" in evidence
