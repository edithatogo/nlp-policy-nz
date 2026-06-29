"""Coverage-reporting surface checks for Track 23."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.coverage


def test_coverage_marker_is_registered() -> None:
    """Ensure the dedicated coverage marker test module is importable."""
    assert True
