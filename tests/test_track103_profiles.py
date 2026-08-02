"""Tests for Track 103 profile schema and fail-closed loading."""

import json
from pathlib import Path

import pytest

from nlp_policy_nz.jurisdiction_profiles import ProfileError, ProfileLoader


ROOT = Path(__file__).resolve().parents[1]


def test_known_profiles_load_with_verified_digests():
    loader = ProfileLoader(ROOT / "config" / "jurisdictions")

    assert loader.load("nz").country == "NZ"
    assert loader.load("au-commonwealth").adapter == "foio_au"
    assert loader.load("nsw").country == "AU-NSW"


def test_unknown_profile_fails_closed():
    with pytest.raises(ProfileError, match="unknown"):
        ProfileLoader(ROOT / "config" / "jurisdictions").load("unknown")


def test_digest_tampering_fails_closed(tmp_path):
    source = ROOT / "config" / "jurisdictions" / "nz.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    data["country"] = "XX"
    profile = tmp_path / "nz.json"
    profile.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ProfileError, match="digest mismatch"):
        ProfileLoader(tmp_path).load("nz")
