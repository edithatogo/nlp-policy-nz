"""Conductor closeout tests for Track 33."""

from __future__ import annotations

import json
from pathlib import Path

TRACK_DIR = Path("conductor/tracks/track33_graph_vector_network_analysis_20260625")


def test_track33_conductor_artifacts_mark_complete() -> None:
    """Track 33 conductor artifacts should reflect implemented status."""
    metadata = json.loads(TRACK_DIR.joinpath("metadata.json").read_text(encoding="utf-8"))
    spec = TRACK_DIR.joinpath("spec.md").read_text(encoding="utf-8")
    plan = TRACK_DIR.joinpath("plan.md").read_text(encoding="utf-8")
    tracks = Path("conductor/tracks.md").read_text(encoding="utf-8")

    assert metadata["status"] == "complete"
    assert "**Status**: Complete" in spec
    assert "**Status**: Complete" in plan
    assert "## [x] Track 33: Graph, Vector, and Network Analysis" in tracks
    assert "- [ ]" not in spec


def test_track33_evidence_names_outputs_and_boundaries() -> None:
    """Track 33 evidence should record outputs and corpus/index limits."""
    evidence = TRACK_DIR.joinpath("evidence.md").read_text(encoding="utf-8")
    index = TRACK_DIR.joinpath("index.md").read_text(encoding="utf-8")

    assert "graph_vector_manifest.json" in evidence
    assert "fixture-bounded" in evidence
    assert "full graph/vector" in evidence
    assert "docs/graph_vector_network_analysis.md" in index
