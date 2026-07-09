"""Tests for Track 34 standards-based publication protocol artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.publication.protocol import (
    PUBLICATION_PROTOCOL_CLAIMS_FILENAME,
    PUBLICATION_PROTOCOL_INVENTORY_FILENAME,
    PUBLICATION_PROTOCOL_MANIFEST_FILENAME,
    PUBLICATION_PROTOCOL_MARKDOWN_FILENAME,
    PUBLICATION_PROTOCOL_OVERCLAIM_FILENAME,
    build_publication_protocol,
    write_publication_protocol_artifacts,
)


def test_publication_protocol_maps_claims_to_evidence_and_boundaries() -> None:
    """Track 34 should separate implemented, external, planned, and blocker claims."""
    bundle = build_publication_protocol()

    assert bundle.manifest["track_id"] == "track34_publication_protocol_20260625"
    assert bundle.manifest["claim_counts"]["repo_evidence"] >= 6
    assert bundle.manifest["claim_counts"]["blocker"] >= 2
    assert bundle.manifest["claim_counts"]["external_gate"] >= 1
    assert all(claim["evidence_paths"] for claim in bundle.claims)
    assert any(
        "data/statistics/corpus_statistics_blockers.json" in claim["evidence_paths"]
        for claim in bundle.claims
        if claim["claim_status"] == "blocker"
    )
    assert "does not claim full-corpus" in bundle.markdown


def test_publication_protocol_inventory_includes_reproducible_artifacts() -> None:
    """The protocol inventory should name reproducible commands and artifacts."""
    bundle = build_publication_protocol()

    assert any(
        item["path"] == "data/analysis/graph_vector_manifest.json"
        for item in bundle.artifact_inventory
    )
    assert any(
        command["command"] == "nlp-policy-nz publication-protocol --output-dir data/publication"
        for command in bundle.reproducibility_commands
    )
    assert any(review["risk_level"] == "high" for review in bundle.overclaim_review)
    assert "Interface surfaces and downstream use" in bundle.markdown
    assert "Comparative tooling and runtime choices" in bundle.markdown
    assert "Data and code availability" in bundle.markdown
    assert "Decision appendix" in bundle.markdown


def test_publication_protocol_writer_round_trips(tmp_path: Path) -> None:
    """Writer should emit deterministic JSON and Markdown protocol artifacts."""
    written = write_publication_protocol_artifacts(tmp_path, markdown_path=tmp_path / "protocol.md")

    assert set(written) == {
        PUBLICATION_PROTOCOL_MANIFEST_FILENAME,
        PUBLICATION_PROTOCOL_CLAIMS_FILENAME,
        PUBLICATION_PROTOCOL_INVENTORY_FILENAME,
        PUBLICATION_PROTOCOL_OVERCLAIM_FILENAME,
        PUBLICATION_PROTOCOL_MARKDOWN_FILENAME,
    }
    manifest = json.loads(written[PUBLICATION_PROTOCOL_MANIFEST_FILENAME].read_text(encoding="utf-8"))
    claims = json.loads(written[PUBLICATION_PROTOCOL_CLAIMS_FILENAME].read_text(encoding="utf-8"))
    markdown = written[PUBLICATION_PROTOCOL_MARKDOWN_FILENAME].read_text(encoding="utf-8")

    assert manifest["artifact_files"]["claims"] == PUBLICATION_PROTOCOL_CLAIMS_FILENAME
    assert len(claims["claims"]) == manifest["claim_counts"]["total"]
    assert "# Standards-Based Publication Protocol" in markdown
    assert "## Reproducibility instructions" in markdown


def test_publication_protocol_cli_writes_artifacts(tmp_path: Path) -> None:
    """The CLI should dispatch to the Track 34 protocol writer."""
    output_dir = tmp_path / "publication"

    rc = main(["publication-protocol", "--output-dir", str(output_dir)])

    assert rc == 0
    assert output_dir.joinpath(PUBLICATION_PROTOCOL_MANIFEST_FILENAME).is_file()
    assert output_dir.joinpath(PUBLICATION_PROTOCOL_CLAIMS_FILENAME).is_file()
    assert output_dir.joinpath(PUBLICATION_PROTOCOL_MARKDOWN_FILENAME).is_file()
