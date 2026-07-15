from __future__ import annotations

import json
from pathlib import Path

import pytest

from nlp_policy_nz.release_engineering import (
    build_version_manifest,
    render_zenodo_metadata,
    render_zenodo_mirror_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_root_zenodo_metadata_matches_current_citation_version() -> None:
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    version = json.loads((ROOT / "VERSION.json").read_text(encoding="utf-8"))["version"]
    assert zenodo["version"] == version
    assert zenodo["title"] == "nlp-policy-nz"


def test_release_assets_render_version_aligned_zenodo_files() -> None:
    manifest = build_version_manifest(
        "1.2.3", "a" * 40, dataset_revision="7", build_timestamp="2026-07-15T00:00:00Z"
    )
    metadata = json.loads(
        render_zenodo_metadata(
            manifest,
            title="nlp-policy-nz",
            authors=["Maintainer"],
            description="Release",
            repository_url="https://example.test/repo",
        )
    )
    mirror = json.loads(render_zenodo_mirror_manifest(manifest))
    assert metadata["version"] == "1.2.3"
    assert mirror["publication_status"] == "unverified"
    assert mirror["version_doi"] is None
    assert mirror["concept_doi"] is None


def test_verified_mirror_requires_live_evidence() -> None:
    manifest = build_version_manifest("1.2.3", "a" * 40, dataset_revision="7")
    with pytest.raises(ValueError, match="verified Zenodo evidence"):
        render_zenodo_mirror_manifest(manifest, verified=True)

    mirror = json.loads(
        render_zenodo_mirror_manifest(
            manifest,
            version_doi="10.5281/zenodo.123",
            concept_doi="10.5281/zenodo.456",
            record_url="https://zenodo.org/records/123",
            verified=True,
        )
    )
    assert mirror["publication_status"] == "verified"
    assert mirror["version_doi"] == "10.5281/zenodo.123"
