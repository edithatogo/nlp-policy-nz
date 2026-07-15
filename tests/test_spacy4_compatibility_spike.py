"""Regression tests for the isolated spaCy 4 compatibility spike."""

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_spacy4_evidence_keeps_production_on_stable_spacy3() -> None:
    """The evidence contract must record a no-switch production decision."""
    evidence = json.loads(
        (ROOT / "artifacts/track104/spacy4_compatibility_spike.json").read_text(encoding="utf-8")
    )
    assert evidence["status"] == "candidate_blocked"
    assert evidence["production_policy"]["switch_to_spacy4"] is False
    assert evidence["production_policy"]["spacy_spec"] == ">=3.7.0 (locked baseline 3.8.14),<4.0.0"
    assert evidence["baseline"]["span_count"] > 0
    assert evidence["baseline"]["serialization_sha256"]
    assert evidence["baseline"]["accuracy"]["status"] == "not_measured"
    assert evidence["candidate"]["status"] == "blocked"
    detail = evidence["candidate"]["detail"]
    assert any(
        marker in detail
        for marker in ("numpy.dtype size changed", "OpenBLAS error", "binary incompatibility")
    )
