"""Citation and Zenodo mirroring contract tests."""

from __future__ import annotations

from scripts.check_citation_mirror import check


def test_citation_zenodo_mirror_contract() -> None:
    assert check() == []
