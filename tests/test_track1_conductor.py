"""Conductor archive checks for Track 1 environment setup."""

from __future__ import annotations

import json
from pathlib import Path

TRACK1 = Path("conductor/tracks/archive/track1_env_setup_20260609")


def test_track1_conductor_artifacts_are_archived() -> None:
    """Track 1 should remain discoverable after archive cleanup."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK1.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK1.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK1.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 1: Initialize Workspace Environment & Quality Tooling (archived)" in registry
    assert str(TRACK1).replace("\\", "/") in registry
    assert metadata["track_id"] == "track1_env_setup_20260609"
    assert metadata["status"] == "archived"
    assert "Phase 1: Environment & Build System Setup" in plan
    assert "Configure `pyproject.toml` with `hatchling`" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK1.joinpath(required_file).is_file()


def test_track1_evidence_links_foundational_tooling() -> None:
    """Evidence should preserve the setup and quality-gate surface."""
    evidence = TRACK1.joinpath("evidence.md").read_text(encoding="utf-8")

    for expected in ("pixi.toml", "pyproject.toml", "Ruff", "Vale", "GitHub Actions"):
        assert expected in evidence
