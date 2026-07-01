"""Tests for Track 34 standards-based publication protocol artifacts."""

from __future__ import annotations

import json
from pathlib import Path

EVIDENCE_MAP = Path("data/publication/track34_protocol_evidence_map.json")
PROTOCOL = Path("docs/publication_protocol.md")


def test_publication_protocol_claims_are_evidence_bound() -> None:
    """Each Track 34 claim should have explicit support and safe wording."""
    payload = json.loads(EVIDENCE_MAP.read_text(encoding="utf-8"))

    assert payload["track_id"] == "track34_publication_protocol_20260625"
    assert payload["claims"]
    assert "fixture-bounded" in " ".join(payload["overclaim_guardrails"])

    allowed_statuses = {"repo_evidence", "external_evidence", "planned_work", "blocker"}
    claim_ids = {claim["claim_id"] for claim in payload["claims"]}
    assert {
        "pipeline-architecture",
        "standards-coverage",
        "rules-as-code-bridge",
        "statistics-boundary",
        "graph-vector-boundary",
        "reproducibility",
    } <= claim_ids

    for claim in payload["claims"]:
        assert claim["status"] in allowed_statuses
        assert claim["evidence"], claim["claim_id"]
        assert claim["publication_wording"], claim["claim_id"]
        if claim["status"] == "repo_evidence":
            for evidence_path in claim["evidence"]:
                assert Path(evidence_path).exists(), evidence_path
        if claim["status"] == "blocker":
            assert claim.get("blockers"), claim["claim_id"]


def test_publication_protocol_documents_required_sections_and_guardrails() -> None:
    """The protocol document should cover the Track 34 acceptance criteria."""
    text = PROTOCOL.read_text(encoding="utf-8")

    required_sections = (
        "# Standards-Based Publication Protocol",
        "## Repository overview",
        "## Reproducibility instructions",
        "## Evidence classes",
        "## Standards compliance matrix",
        "## Ontology and reasoning strategy",
        "## Rules-as-code bridge",
        "## Corpus statistics methodology",
        "## Graph and vector methodology",
        "## Artifact inventory",
        "## Limitations and blocker policy",
        "## Overclaim review checklist",
    )
    for section in required_sections:
        assert section in text

    assert "fixture-bounded" in text
    assert "must not claim executable rules-as-code behavior" in text
    assert "data/publication/track34_protocol_evidence_map.json" in text


def test_publication_protocol_artifact_inventory_paths_exist() -> None:
    """Machine-readable artifact inventory should point to existing artifacts."""
    payload = json.loads(EVIDENCE_MAP.read_text(encoding="utf-8"))
    inventory = payload["artifact_inventory"]

    assert Path(inventory["protocol_document"]).is_file()
    assert Path(inventory["evidence_map"]).is_file()
    for paths in (
        inventory["standards_inputs"],
        inventory["analysis_inputs"],
        inventory["quality_inputs"],
    ):
        for artifact in paths:
            assert Path(artifact).exists(), artifact
