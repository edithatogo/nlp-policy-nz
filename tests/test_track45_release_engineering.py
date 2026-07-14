"""Track 45 release engineering contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.release_engineering import (
    build_version_manifest,
    calculate_next_version,
    prepend_changelog_entry,
    render_citation_cff,
)

ROOT = Path(__file__).resolve().parents[1]
TRACK45 = ROOT / "conductor" / "tracks" / "track45_release_engineering_20260626"


def test_track45_release_artifacts_exist() -> None:
    """Track 45 should ship release metadata, workflows, and docs."""
    expected = [
        ROOT / "CHANGELOG.md",
        ROOT / "CITATION.cff",
        ROOT / "VERSION.json",
        ROOT / ".github" / "workflows" / "publish-hf-datasets.yml",
        ROOT / ".github" / "workflows" / "publish-hf-models.yml",
        ROOT / ".github" / "workflows" / "publish-hf-space.yml",
        ROOT / ".github" / "workflows" / "publish-zenodo.yml",
        ROOT / ".github" / "workflows" / "publish-osf.yml",
        ROOT / ".github" / "workflows" / "publish-pypi.yml",
        ROOT / ".github" / "workflows" / "release.yml",
        ROOT / "scripts" / "release_metadata.py",
        TRACK45 / "index.md",
        TRACK45 / "metadata.json",
        TRACK45 / "plan.md",
        TRACK45 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track45_registry_metadata_and_plan_are_in_sync() -> None:
    """Track 45 should be tracked as in progress with release-specific scope."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK45 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK45 / "plan.md").read_text(encoding="utf-8")
    spec = (TRACK45 / "spec.md").read_text(encoding="utf-8")

    assert "Track 45: Release Engineering & Automated Publishing" in registry
    assert "./conductor/tracks/track45_release_engineering_20260626/" in registry
    assert metadata["track_id"] == "track45_release_engineering_20260626"
    assert metadata["status"] == "complete"
    assert "VERSION.json" in plan
    assert "CITATION.cff" in plan
    assert "publish-hf-datasets.yml" in plan
    assert "publish-hf-models.yml" in plan
    assert "semantic versioning" in spec.lower()
    assert "pypi" in spec.lower()
    assert "CITATION.cff" in spec


def test_track45_release_helpers_cover_versioning_manifest_and_changelog(
    tmp_path: Path,
) -> None:
    """Release helpers should bump versions, render metadata, and update changelogs."""
    assert calculate_next_version("0.1.0", ["feat: add release metadata"]) == "0.2.0"
    assert calculate_next_version("0.1.0", ["fix: patch release workflow"]) == "0.1.1"
    assert calculate_next_version("1.2.3", ["feat!: break release format"]) == "2.0.0"
    assert calculate_next_version("1.2.3", ["docs: clarify release steps"]) == "1.2.4"

    manifest = build_version_manifest(
        "1.2.3",
        "abc1234",
        dataset_revision="7",
        build_timestamp="2026-07-02T00:00:00Z",
    )
    assert manifest == {
        "version": "1.2.3",
        "build_timestamp": "2026-07-02T00:00:00Z",
        "commit_sha": "abc1234",
        "dataset_revision": "7",
    }

    citation = render_citation_cff(
        manifest,
        title="nlp-policy-nz",
        authors=["Maintainer"],
        repository_url="https://example.test/nlp-policy-nz",
        doi="10.1234/example",
    )
    assert "cff-version: 1.2.0" in citation
    assert 'title: "nlp-policy-nz"' in citation
    assert 'version: "1.2.3"' in citation
    assert 'repository-code: "https://example.test/nlp-policy-nz"' in citation
    assert 'doi: "10.1234/example"' in citation
    assert 'name: "Maintainer"' in citation

    changelog = tmp_path / "CHANGELOG.md"
    prepend_changelog_entry(changelog, version="1.2.3", release_notes="* Added release metadata")
    rendered = changelog.read_text(encoding="utf-8")
    assert rendered.startswith("# Changelog")
    assert "## v1.2.3" in rendered
    assert "* Added release metadata" in rendered
