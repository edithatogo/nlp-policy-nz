"""Conductor contract tests for Track 49."""

from __future__ import annotations

import json
from pathlib import Path

TRACK49 = Path("conductor/tracks/archive/track49_documentation_site_20260626")


def test_track49_conductor_registry_and_metadata_are_complete() -> None:
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK49.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK49.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK49.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 49: Documentation Site & Knowledge Base (archived)" in registry
    assert str(TRACK49).replace("\\", "/") in registry
    assert metadata["track_id"] == "track49_documentation_site_20260626"
    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    assert plan.count("[x]") >= 9
    assert spec.count("[x]") >= 7


def test_track49_evidence_links_required_artifacts() -> None:
    evidence = TRACK49.joinpath("evidence.md").read_text(encoding="utf-8")
    required = (
        "docs-site/astro.config.mjs",
        ".github/workflows/docs.yml",
        "scripts/generate_docs_reference.py",
        "docs-site/src/content/docs/index.md",
        "docs-site/src/content/docs/api/openapi.md",
        "docs-site/src/content/docs/operations/runbook.md",
        "docs/notebooks/hansard_stance_citations.ipynb",
        "tests/test_track49_docs_site.py",
    )

    for path in required:
        assert Path(path).is_file()
        assert path in evidence
