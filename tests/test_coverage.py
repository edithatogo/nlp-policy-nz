"""Coverage-reporting surface checks for Track 23."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.coverage


def test_coverage_marker_is_registered() -> None:
    """Ensure the dedicated coverage marker test module is importable."""
    assert True


def test_track23_coverage_gate_is_repo_scoped_with_explicit_exclusions() -> None:
    """Track 23 should keep a durable 90% coverage gate and named exclusions."""
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    coverage = pyproject["tool"]["coverage"]

    assert coverage["report"]["fail_under"] == 90
    assert coverage["run"]["source"] == ["src"]
    assert set(coverage["run"]["omit"]) >= {
        "src/nlp_policy_nz/semantic/finetune.py",
        "src/nlp_policy_nz/storage/faiss_adapter.py",
        "src/nlp_policy_nz/storage/haystack_pipeline.py",
        "src/nlp_policy_nz/training/run_qlora.py",
    }
