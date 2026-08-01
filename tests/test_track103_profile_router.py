"""Tests for explicit Track 103 profile-backed adapter routing."""

from pathlib import Path

import pytest

from nlp_policy_nz.extraction.profile_router import load_profile_adapter
from nlp_policy_nz.jurisdiction_profiles import ProfileError, ProfileLoader


ROOT = Path(__file__).resolve().parents[1]


def test_profile_ids_route_to_existing_adapters():
    loader = ProfileLoader(ROOT / "config" / "jurisdictions")

    assert load_profile_adapter("nz", loader=loader).__name__.endswith("foio_nz_adapter")
    assert load_profile_adapter("nsw", loader=loader).__name__.endswith("foio_au_adapter")


def test_unknown_profile_does_not_fall_back_to_nz():
    with pytest.raises(ProfileError):
        load_profile_adapter("uk", loader=ProfileLoader(ROOT / "config" / "jurisdictions"))
