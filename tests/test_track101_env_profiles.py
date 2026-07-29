"""Regression tests for Track 101 environment-profile handling."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_secret_environment_profiles_are_ignored():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    for filename in (".env.dev", ".env.staging", ".env.prod"):
        assert filename in ignore.splitlines()


def test_quickstart_warns_against_committing_profile_secrets():
    quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")

    assert ".env.staging" in quickstart
    assert "out of version control" in quickstart
