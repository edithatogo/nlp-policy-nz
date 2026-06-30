from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_version_consistency import SEMVER_RE, check_version_consistency  # noqa: E402


@pytest.mark.unit
def test_version_consistency_check_passes() -> None:
    assert check_version_consistency() == []


@pytest.mark.unit
def test_version_is_well_formed() -> None:
    version = _pyproject_version()
    assert SEMVER_RE.fullmatch(version)


def _pyproject_version() -> str:
    import tomllib

    return str(
        tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8-sig"))["project"]["version"]
    )
