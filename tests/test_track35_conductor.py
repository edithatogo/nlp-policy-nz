"""Conductor closeout tests for Track 35."""

from __future__ import annotations

import json
from pathlib import Path

TRACK_DIR = Path("conductor/tracks/track35_analysis_artifact_execution_20260625")


def test_track35_conductor_artifacts_mark_complete() -> None:
    """Track 35 conductor artifacts should reflect implemented status."""
    metadata = json.loads(TRACK_DIR.joinpath("metadata.json").read_text(encoding="utf-8"))
    spec = TRACK_DIR.joinpath("spec.md").read_text(encoding="utf-8")
    plan = TRACK_DIR.joinpath("plan.md").read_text(encoding="utf-8")
    tracks = Path("conductor/tracks.md").read_text(encoding="utf-8")

    assert metadata["status"] == "complete"
    assert "**Status**: Complete" in spec
    assert "**Status**: Complete" in plan
    assert "## [x] Track 35: Analysis Artifact Execution and Figure Production" in tracks
    assert "- [ ]" not in spec


def test_track35_evidence_names_artifacts_and_blockers() -> None:
    """Track 35 evidence should record outputs and full-corpus limits."""
    evidence = TRACK_DIR.joinpath("evidence.md").read_text(encoding="utf-8")
    index = TRACK_DIR.joinpath("index.md").read_text(encoding="utf-8")

    assert "analysis_artifact_manifest.json" in evidence
    assert "embedding_projection.svg" in evidence
    assert "full citation graph" in evidence
    assert "scripts/generate_all_artifacts.py" in index
