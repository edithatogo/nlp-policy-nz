from __future__ import annotations

import json
from pathlib import Path

TRACK54 = Path("conductor/tracks/archive/track54_axiom_foundation_interop_20260629")


def _read(name: str) -> str:
    return TRACK54.joinpath(name).read_text(encoding="utf-8")


def test_track54_conductor_track_is_registered_and_complete() -> None:
    metadata = json.loads(_read("metadata.json"))
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")

    assert metadata["track_id"] == "track54_axiom_foundation_interop_20260629"
    assert metadata["status"] == "archived"
    assert metadata["type"] == "feature"
    assert str(TRACK54).replace("\\", "/") in registry
    assert "## [x] Track 54: Axiom Foundation Interoperability (archived)" in registry

    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK54.joinpath(required_file).is_file()

    index = _read("index.md")
    assert "evidence.md" in index


def test_track54_records_offline_axiom_integration_boundaries() -> None:
    spec = _read("spec.md")
    plan = _read("plan.md")
    evidence = _read("evidence.md")
    docs = Path("docs/axiom-foundation-relevance.md").read_text(encoding="utf-8")

    for phrase in (
        "without vendoring Axiom repositories",
        "depend on the executable RuleSpec runtime",
        "Fetching, cloning, or executing Axiom repositories as part of default tests",
    ):
        assert phrase in spec

    assert "Live execution through `axiom-rules-engine` remains out of scope" in plan
    assert "Raw URL, retrieval timestamp, and checksum pins are kept" in evidence
    assert "Don't copy Axiom repositories" in docs


def test_track54_evidence_captures_rulespec_nz_compatibility_and_full_gate() -> None:
    evidence = _read("evidence.md")

    for phrase in (
        "rulespec-nz Compatibility Review",
        "corpus_citation_path",
        "module.source_verification.source_url",
        "pixi.exe' run check",
        "pytest reported 666 passed, 1 skipped",
    ):
        assert phrase in evidence


def test_track54_does_not_add_axiom_runtime_dependencies() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
    pixi = Path("pixi.toml").read_text(encoding="utf-8")
    combined = f"{pyproject}\n{pixi}"

    for package in (
        "axiom-rules-engine",
        "axiom-corpus",
        "axiom-scrapers",
        "axiom-encode",
        "rulespec-nz",
    ):
        assert package not in combined
