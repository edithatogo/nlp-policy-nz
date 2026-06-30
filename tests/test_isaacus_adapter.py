"""Tests for Track 22 Isaacus ecosystem integration helpers."""

from __future__ import annotations

import copy
import json
import unicodedata
from pathlib import Path

import pytest

from nlp_policy_nz.storage.serialization import PipelineRecord
from nlp_policy_nz.training.isaacus_adapter import (
    IsaacusAccessGate,
    default_isaacus_datasets,
    default_isaacus_models,
    default_isaacus_tools,
    load_nz_mleb_fixture,
    main,
    make_nz_mleb_query,
    normalize_isaacus_record,
    normalize_isaacus_records,
    render_isaacus_integration_report,
    render_isaacus_manifest_json,
    require_external_access,
    to_pipeline_record,
    validate_nz_mleb_fixture,
)

ROOT = Path(__file__).resolve().parents[1]
TRACK22_FIXTURE = ROOT / "data" / "track22" / "nz_mleb_fixture.json"
TRACK22_SCHEMA = ROOT / "data" / "track22" / "nz_mleb_fixture.schema.json"


def test_default_manifests_cover_required_isaacus_assets() -> None:
    """The offline registry captures the Track 22 dataset, model, and tool scope."""
    datasets = default_isaacus_datasets()
    models = default_isaacus_models()
    tools = default_isaacus_tools()

    assert {"open-australian-legal-corpus", "open-australian-legal-qa"} <= set(datasets)
    assert {"legal-rag-bench", "mleb-legal-rag-bench"} <= set(datasets)
    assert datasets["open-australian-legal-corpus"].expected_records == 147_000
    assert "open-australian-legal-llm" in models
    assert models["kanon-2-embedder"].access_mode == "api-or-airgapped"
    assert tools["semchunk"].integration_action == "evaluate"
    assert tools["blackstone-graph"].integration_action == "monitor"


def test_normalize_isaacus_record_preserves_legal_and_maori_text() -> None:
    """Australian source rows are normalised without damaging macron text."""
    row = {
        "id": "NSW-001",
        "title": "Evidence Act extract",
        "text": "The court must consider tikanga Ma\u0304ori.\n\nSection 12 applies.",
        "jurisdiction": "NSW",
        "citation": "Evidence Act 1995 (NSW) s 12",
        "source_url": "https://example.test/nsw-001",
    }

    record = normalize_isaacus_record("open-australian-legal-corpus", row)

    assert record.source_id == "open-australian-legal-corpus"
    assert record.doc_id == "NSW-001"
    assert record.jurisdiction == "NSW"
    assert record.citations == ("Evidence Act 1995 (NSW) s 12",)
    assert "tikanga Māori" in record.text
    assert unicodedata.is_normalized("NFC", record.text)


def test_to_pipeline_record_maps_au_corpus_into_existing_schema() -> None:
    """Normalised Isaacus records are converted into existing PipelineRecord rows."""
    isaacus_record = normalize_isaacus_record(
        "open-australian-legal-corpus",
        {
            "id": "HCA-42",
            "text": "A person may appeal under the Migration Act.",
            "jurisdiction": "HCA",
            "citations": ["Migration Act 1958 (Cth)"],
        },
    )

    pipeline_record = to_pipeline_record(isaacus_record)

    assert isinstance(pipeline_record, PipelineRecord)
    assert pipeline_record.doc_id == "isaacus:open-australian-legal-corpus:HCA-42"
    assert pipeline_record.corpus_source == "isaacus:au:HCA"
    assert pipeline_record.nz_act_citations == ["Migration Act 1958 (Cth)"]
    assert pipeline_record.cleaned_tokens[:3] == ["A", "person", "may"]


def test_normalize_records_handles_missing_optional_citations_and_batching() -> None:
    """Batch normalisation works when optional citation fields are absent."""
    records = normalize_isaacus_records(
        "open-australian-legal-corpus",
        [
            {
                "doc_id": "AU-1",
                "body": "Tikanga Māori is discussed in comparative context.",
                "court": "Cth",
            }
        ],
    )

    assert len(records) == 1
    assert records[0].doc_id == "isaacus:open-australian-legal-corpus:AU-1"
    assert records[0].nz_act_citations == []
    assert records[0].te_reo_terms == ["Māori"]


def test_normalize_record_rejects_missing_required_fields() -> None:
    """Rows without identifiers or text fail before entering the pipeline."""
    with pytest.raises(ValueError, match="identifier"):
        normalize_isaacus_record("open-australian-legal-corpus", {"text": "body"})

    with pytest.raises(ValueError, match="text"):
        normalize_isaacus_record("open-australian-legal-corpus", {"id": "AU-2"})


def test_make_nz_mleb_query_validates_relevance_judgements() -> None:
    """MLEB-NZ task scaffolds require at least one relevant document."""
    query = make_nz_mleb_query(
        query_id="nz-citation-001",
        query_text="What provision governs tikanga evidence?",
        relevant_doc_ids=["nz-act-7", "hca-42"],
        jurisdiction="NZ",
        task="citation-search",
    )

    assert query.query_id == "nz-citation-001"
    assert query.relevant_doc_ids == ("nz-act-7", "hca-42")

    with pytest.raises(ValueError, match="relevant document"):
        make_nz_mleb_query(
            query_id="bad",
            query_text="empty",
            relevant_doc_ids=[],
            jurisdiction="NZ",
            task="citation-search",
        )


def test_local_nz_mleb_fixture_matches_schema_contract() -> None:
    """Track 22 ships deterministic local queries and relevance judgements."""
    payload = json.loads(TRACK22_FIXTURE.read_text(encoding="utf-8"))
    schema = json.loads(TRACK22_SCHEMA.read_text(encoding="utf-8"))

    queries = load_nz_mleb_fixture(TRACK22_FIXTURE)

    assert schema["properties"]["schema_version"]["const"] == payload["schema_version"]
    assert payload["jurisdiction"] == "NZ"
    assert len(payload["documents"]) == 3
    assert len(payload["queries"]) == 3
    assert {query.task for query in queries} == {
        "citation-search",
        "policy-similarity",
        "case-retrieval",
    }
    assert queries[0].query_id == "nz-mleb-001"
    assert queries[0].relevant_doc_ids == (
        "nz-leg-te-ture-whenua-1993-s2",
        "nz-case-ellis-2022-tikanga",
    )


def test_local_nz_mleb_fixture_validation_rejects_bad_judgements() -> None:
    """The local fixture contract fails on broken relevance judgements."""
    payload = json.loads(TRACK22_FIXTURE.read_text(encoding="utf-8"))
    broken = copy.deepcopy(payload)
    broken["queries"][0]["judgements"][0]["doc_id"] = "missing-doc"

    with pytest.raises(ValueError, match="unknown document"):
        validate_nz_mleb_fixture(broken)

    broken = copy.deepcopy(payload)
    broken["queries"][1]["judgements"] = []

    with pytest.raises(ValueError, match="requires judgements"):
        validate_nz_mleb_fixture(broken)


def test_external_access_gate_is_explicit_and_report_is_repo_side() -> None:
    """Download/evaluation gates fail closed unless explicitly configured."""
    gate = IsaacusAccessGate(allow_network=False, allow_proprietary_api=False)

    with pytest.raises(PermissionError, match="network access"):
        require_external_access(gate, needs_network=True, needs_proprietary_api=False)

    with pytest.raises(PermissionError, match="proprietary API access"):
        require_external_access(
            IsaacusAccessGate(allow_network=True, allow_proprietary_api=False),
            needs_network=True,
            needs_proprietary_api=True,
        )

    require_external_access(
        IsaacusAccessGate(allow_network=True, allow_proprietary_api=True),
        needs_network=True,
        needs_proprietary_api=True,
    )

    report = render_isaacus_integration_report()

    assert "repo-side integration scaffold" in report
    assert "No Isaacus datasets or models are downloaded by this report" in report
    assert "open-australian-legal-corpus" in report
    assert "kanon-2-embedder" in report


def test_manifest_json_and_cli_entrypoints(capsys: pytest.CaptureFixture[str]) -> None:
    """The offline CLI prints deterministic manifest and report outputs."""
    manifest_json = render_isaacus_manifest_json()

    assert '"open-australian-legal-corpus"' in manifest_json
    assert main(["--print-manifest"]) == 0
    assert "open-australian-legal-corpus" in capsys.readouterr().out

    assert main(["--report"]) == 0
    assert "repo-side integration scaffold" in capsys.readouterr().out

    assert main([]) == 0
    assert "usage:" in capsys.readouterr().out
