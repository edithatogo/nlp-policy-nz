"""Tests for the optional read-only MCP adapter surface."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.axiom import SourceSection
from nlp_policy_nz.mcp import build_mcp_manifest, call_tool, main, read_resource
from nlp_policy_nz.provenance import ProvenanceRecorder, provenance_sidecar_path
from nlp_policy_nz.quality.monitoring import build_quality_report, report_to_json
from nlp_policy_nz.storage import PipelineRecord


def _pipeline_record() -> PipelineRecord:
    return PipelineRecord(
        doc_id="doc-1",
        corpus_source="legislation",
        raw_text="The Minister must report to Parliament.",
        cleaned_tokens=["The", "Minister", "must", "report", "to", "Parliament"],
        nz_act_citations=["nz/statutes/example-act/2026/1"],
        te_reo_terms=[],
        legal_effect="obligation",
    )


def _source_section() -> SourceSection:
    return SourceSection.from_text(
        "A person must keep records.",
        citation_path="nz/statutes/example-act/2026/14",
        jurisdiction="NZ",
        document_type="act",
        source_url="https://legislation.govt.nz/example-act/section/14",
        retrieved_at="2026-06-29T00:00:00Z",
        title="Example Act 2026, section 14",
    )


def test_manifest_exposes_read_only_tools_resources_and_track81_mapping() -> None:
    manifest = build_mcp_manifest()

    assert manifest["server_name"] == "nlp-policy-nz"
    assert manifest["contract_id"] == "nlp-policy-nz.interface-contract.v1"
    assert {tool["name"] for tool in manifest["tools"]} == {
        "search_catalog",
        "inspect_provenance",
        "inspect_quality_report",
        "summarize_ontology",
        "summarize_knowledge_graph",
        "inspect_rules_as_code_candidates",
        "inspect_multi_engine_parity",
    }
    assert {resource["name"] for resource in manifest["resources"]} == {
        "capability_registry",
        "tool_schemas",
        "resource_schemas",
        "generated_docs",
        "track81_status",
        "track84_status",
    }
    assert all(tool["side_effect"] == "read_only" for tool in manifest["tools"])
    assert all(resource["side_effect"] == "read_only" for resource in manifest["resources"])
    assert all(tool["capability_ids"] for tool in manifest["tools"])
    assert manifest["capability_registry"]["entry_count"] == len(
        manifest["interface_contract"]["capabilities"]
    )


def test_resource_payloads_include_schemas_docs_and_conductor_artifacts() -> None:
    tool_schemas = read_resource("tool_schemas")
    resource_schemas = read_resource("resource_schemas")
    docs = read_resource("generated_docs")
    track81 = read_resource("track81_status")
    track84 = read_resource("track84_status")

    assert tool_schemas["tools"][0]["name"] == "search_catalog"
    assert resource_schemas["by_name"]["capability_registry"]["uri"].startswith("nlp-policy-nz://")
    assert "Read-only tools and resources" in docs["markdown"]
    assert "Track 81" in track81["files"]["spec.md"]
    assert "Track 84" in track84["files"]["spec.md"]


def test_search_and_provenance_calls_delegate_to_core_helpers(tmp_path: Path) -> None:
    recorder = ProvenanceRecorder(
        pipeline_name="process_legislation",
        pipeline_version="1.0.0",
        model_versions={},
        parameters={},
        commit_sha="abc1234",
    )
    provenance = recorder.finish(
        input_paths=[tmp_path / "input.xml"],
        output_path=tmp_path / "output.parquet",
        record_count=1,
    )
    sidecar = provenance.write_sidecar()

    search = call_tool("search_catalog", query="provenance", limit=3)
    provenance_result = call_tool("inspect_provenance", path=str(sidecar))

    assert search["query"] == "provenance"
    assert any(match["id"] == "inspect_provenance" for match in search["matches"])
    assert provenance_result["summary"]["type"] == "prov:Bundle"
    assert provenance_result["sidecar_path"] == str(sidecar.resolve())


def test_quality_ontology_and_parity_calls_are_fixture_bounded(tmp_path: Path) -> None:
    record = _pipeline_record()
    report = build_quality_report((record,))
    report_path = tmp_path / "quality-report.json"
    report_path.write_text(report_to_json(report), encoding="utf-8")

    quality = call_tool("inspect_quality_report", path=str(report_path))
    ontology = call_tool("summarize_ontology")
    knowledge_graph = call_tool("summarize_knowledge_graph")
    rac_candidates = call_tool("inspect_rules_as_code_candidates")
    parity = call_tool("inspect_multi_engine_parity")

    assert quality["summary"]["record_count"] == 1
    assert ontology["track25"]["row_count"] > 0
    assert knowledge_graph["track31"]["concept_count"] > 0
    assert rac_candidates["summary"]["record_count"] >= 1
    assert parity["report"]["passed"] is True


def test_manifest_entrypoint_prints_json_without_optional_mcp_dependency(capsys) -> None:
    rc = main(["--manifest"])

    captured = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert captured["server_name"] == "nlp-policy-nz"
