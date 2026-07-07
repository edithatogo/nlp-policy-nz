"""Tests for Track 27 rules-as-code bridge scaffolding."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from nlp_policy_nz.axiom import SourceSection
from nlp_policy_nz.cli.main import main
from nlp_policy_nz.extraction import (
    build_rules_as_code_candidate_bundle_from_extraction_manifest,
    build_rules_as_code_candidate_bundle_from_source_inventory,
)
from nlp_policy_nz.ontology import (
    NormSemantics,
    PolicyEnginePackageSkeleton,
    PolicyTaxonomy,
    RulesAsCodeBridgeRecord,
    SourceAnchor,
    TemporalValidity,
    build_policyengine_package_skeleton,
    build_rules_as_code_bridge,
    render_rules_as_code_bridge_json,
    write_policyengine_package_skeleton,
    write_rules_as_code_bridge_json,
)

if TYPE_CHECKING:
    from pathlib import Path


def _contains_key(value: object, key: str) -> bool:
    """Return whether a nested JSON-like value contains *key*."""
    if isinstance(value, dict):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


def _source_section() -> SourceSection:
    """Return a deterministic NZ source section fixture."""
    return SourceSection.from_text(
        "Section 10 Duty. A person must provide information within 20 working days.",
        citation_path="nz/statutes/example-act/2026/10",
        jurisdiction="NZ",
        document_type="act",
        source_url="https://legislation.govt.nz/example-act/section/10",
        retrieved_at="2026-06-29T00:00:00Z",
        title="Example Act 2026, section 10",
        effective_date="2026-07-01",
    )


def test_rules_as_code_bridge_preserves_source_norm_and_rulespec_metadata() -> None:
    """Bridge records connect source anchor, norm semantics, and RuleSpec IDs."""
    record = build_rules_as_code_bridge(
        _source_section(),
        taxonomy=PolicyTaxonomy(
            scheme_id="nz-local-policy-domain",
            concept_id="public-administration",
            label="Public administration",
        ),
        temporal_validity=TemporalValidity(start="2026-07-01", expression="from 1 July 2026"),
    )
    payload = record.to_jsonld()

    assert payload["@type"] == "legalruleml:RuleStatement"
    assert payload["@id"] == "nz:statutes/example-act/2026/10#obligation"
    assert payload["source_anchor"]["source_sha256"] == _source_section().metadata.checksum_sha256
    assert payload["norm_semantics"]["legal_effect"] == "obligation"
    assert payload["norm_semantics"]["trigger"] == "must"
    assert payload["temporal_validity"]["start"] == "2026-07-01"
    assert payload["taxonomy"]["concept_id"] == "public-administration"
    assert payload["rulespec"]["module"]["source_verification"]["corpus_citation_path"] == (
        "nz/statutes/example-act/2026/10"
    )
    assert not _contains_key(payload["rulespec"]["module"], "source_url")
    assert payload["rulespec"]["provenance"]["authoritative_source_url"] == (
        "https://legislation.govt.nz/example-act/section/10"
    )
    assert payload["schema_legislation"]["@type"] == "schema:Legislation"


def test_rules_as_code_bridge_json_is_stable_and_writable(tmp_path: Path) -> None:
    """Bridge JSON renders deterministically and round-trips through disk."""
    record = build_rules_as_code_bridge(_source_section(), concept="information duty")
    rendered = render_rules_as_code_bridge_json(record)
    path = write_rules_as_code_bridge_json(record, tmp_path / "bridge.json")

    loaded = json.loads(path.read_text(encoding="utf-8"))

    assert json.loads(rendered) == loaded
    assert loaded["@id"] == "nz:statutes/example-act/2026/10#information_duty"
    assert loaded["provenance"]["prov:wasGeneratedBy"] == "nlp-policy-nz.rules-as-code-bridge"


def test_rules_as_code_bridge_records_validate_direct_identity_fields() -> None:
    """Direct bridge dataclasses should reject malformed export identities."""
    with pytest.raises(ValueError, match="source_sha256"):
        SourceAnchor(
            citation_path="nz/statutes/example-act/2026/10",
            source_url="https://legislation.govt.nz/example-act/section/10",
            source_sha256="ABC",
        )

    with pytest.raises(ValueError, match="document_type"):
        SourceAnchor(
            citation_path="nz/statutes/example-act/2026/10",
            source_url="https://legislation.govt.nz/example-act/section/10",
            source_sha256="0" * 64,
            document_type="webpage",
        )

    with pytest.raises(ValueError, match="concept_id is required"):
        PolicyTaxonomy(
            scheme_id="nz-local-policy-domain",
            concept_id=" ",
            label="Public administration",
        )

    with pytest.raises(ValueError, match="rulespec_reference"):
        RulesAsCodeBridgeRecord(
            record_id="nz/statutes/example-act/2026/10",
            source_anchor=SourceAnchor(
                citation_path="nz/statutes/example-act/2026/10",
                source_url="https://legislation.govt.nz/example-act/section/10",
                source_sha256="0" * 64,
            ),
            norm_semantics=NormSemantics(legal_effect="obligation"),
            temporal_validity=TemporalValidity(start="2026-07-01"),
            taxonomy=PolicyTaxonomy(
                scheme_id="nz-local-policy-domain",
                concept_id="public-administration",
                label="Public administration",
            ),
            rulespec={},
            schema_legislation={"@type": "schema:Legislation"},
        )


def test_rac_export_cli_writes_bridge_json(tmp_path: Path) -> None:
    """CLI command emits the same offline bridge shape used by Track 27."""
    source = tmp_path / "section.txt"
    output = tmp_path / "rac.json"
    source.write_text("A person may apply for review.", encoding="utf-8")

    rc = main(
        [
            "rac-export",
            "--input",
            str(source),
            "--output",
            str(output),
            "--citation-path",
            "nz/statutes/example-act/2026/12",
            "--source-url",
            "https://legislation.govt.nz/example-act/section/12",
            "--retrieved-at",
            "2026-06-29T00:00:00Z",
            "--title",
            "Example Act 2026, section 12",
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))

    assert rc == 0
    assert payload["@id"] == "nz:statutes/example-act/2026/12#permission"
    assert payload["norm_semantics"]["legal_effect"] == "permission"
    assert not _contains_key(payload["rulespec"]["module"], "source_url")
    assert payload["rulespec"]["provenance"]["authoritative_source_url"] == (
        "https://legislation.govt.nz/example-act/section/12"
    )


def test_policyengine_package_skeleton_is_source_grounded(tmp_path: Path) -> None:
    """Package skeletons expose source pins and non-executable formula stubs."""
    record = build_rules_as_code_bridge(_source_section(), concept="information duty")
    skeleton = build_policyengine_package_skeleton(
        record,
        package_name="PolicyEngine NZ Example",
    )
    output_dir = write_policyengine_package_skeleton(skeleton, tmp_path / "pkg")

    variable_path = output_dir / "policyengine_nz_example" / "variables" / "generated.py"
    parameter_path = output_dir / "policyengine_nz_example" / "parameters" / "generated.yaml"

    assert skeleton.package_name == "policyengine_nz_example"
    assert skeleton.rulespec_id == "nz:statutes/example-act/2026/10#information_duty"
    assert variable_path.is_file()
    assert parameter_path.is_file()
    assert "SOURCE_CITATION_PATH = 'nz/statutes/example-act/2026/10'" in variable_path.read_text(
        encoding="utf-8"
    )
    assert "NotImplementedError" in variable_path.read_text(encoding="utf-8")
    assert "source_sha256:" in parameter_path.read_text(encoding="utf-8")


def test_policyengine_package_skeleton_avoids_keyword_variable_names() -> None:
    """Generated placeholder variables should remain valid Python syntax."""
    record = build_rules_as_code_bridge(_source_section(), concept="class")
    skeleton = build_policyengine_package_skeleton(record)
    variable_module = skeleton.files["policyengine_nz_generated/variables/generated.py"]

    assert "class class_rule:" in variable_module
    compile(variable_module, "generated.py", "exec")


def test_policyengine_package_skeleton_validates_direct_manifest_fields() -> None:
    """Direct skeleton manifests should retain source-grounded package identity."""
    skeleton = PolicyEnginePackageSkeleton(
        package_name="Class",
        files={"README.md": "Generated package.\n"},
        source_citation_path="nz/statutes/example-act/2026/10",
        rulespec_id="nz:statutes/example-act/2026/10#obligation",
    )

    assert skeleton.package_name == "class_rule"

    with pytest.raises(ValueError, match="files"):
        PolicyEnginePackageSkeleton(
            package_name="policyengine_nz_generated",
            files={},
            source_citation_path="nz/statutes/example-act/2026/10",
            rulespec_id="nz:statutes/example-act/2026/10#obligation",
        )

    with pytest.raises(ValueError, match="source_citation_path"):
        PolicyEnginePackageSkeleton(
            package_name="policyengine_nz_generated",
            files={"README.md": "Generated package.\n"},
            source_citation_path=" ",
            rulespec_id="nz:statutes/example-act/2026/10#obligation",
        )

    with pytest.raises(TypeError, match="file content"):
        PolicyEnginePackageSkeleton(
            package_name="policyengine_nz_generated",
            files={"README.md": 123},  # type: ignore[dict-item]
            source_citation_path="nz/statutes/example-act/2026/10",
            rulespec_id="nz:statutes/example-act/2026/10#obligation",
        )


def test_policyengine_package_writer_rejects_paths_outside_output_dir(tmp_path: Path) -> None:
    """Direct skeleton manifests must not write outside the requested root."""
    traversal = PolicyEnginePackageSkeleton(
        package_name="policyengine_nz_generated",
        files={"../escape.py": "print('escape')\n"},
        source_citation_path="nz/statutes/example-act/2026/10",
        rulespec_id="nz:statutes/example-act/2026/10#obligation",
    )
    absolute = PolicyEnginePackageSkeleton(
        package_name="policyengine_nz_generated",
        files={str(tmp_path / "escape.py"): "print('escape')\n"},
        source_citation_path="nz/statutes/example-act/2026/10",
        rulespec_id="nz:statutes/example-act/2026/10#obligation",
    )

    with pytest.raises(ValueError, match="within output_dir"):
        write_policyengine_package_skeleton(traversal, tmp_path / "pkg")

    with pytest.raises(ValueError, match="relative"):
        write_policyengine_package_skeleton(absolute, tmp_path / "pkg")

    assert not (tmp_path / "escape.py").exists()


def test_rac_export_cli_writes_optional_package_skeleton(tmp_path: Path) -> None:
    """CLI package export writes a reviewed-placeholder package layout."""
    source = tmp_path / "section.txt"
    output = tmp_path / "rac.json"
    package_output = tmp_path / "package"
    source.write_text("A person must keep records.", encoding="utf-8")

    rc = main(
        [
            "rac-export",
            "--input",
            str(source),
            "--output",
            str(output),
            "--citation-path",
            "nz/statutes/example-act/2026/14",
            "--source-url",
            "https://legislation.govt.nz/example-act/section/14",
            "--retrieved-at",
            "2026-06-29T00:00:00Z",
            "--package-output-dir",
            str(package_output),
            "--package-name",
            "PolicyEngine NZ Records",
        ]
    )

    assert rc == 0
    assert (package_output / "policyengine_nz_records" / "variables" / "generated.py").is_file()
    assert (package_output / "policyengine_nz_records" / "parameters" / "generated.yaml").is_file()


def test_batch_rac_candidate_bundle_from_source_inventory_preserves_gaps_and_order() -> None:
    """Batch export should stay fixture-bounded and preserve review gating."""
    bundle = build_rules_as_code_candidate_bundle_from_source_inventory()

    assert bundle.manifest.summary.total_records == 5
    assert len(bundle.manifest.summary.known_gaps) == 5
    assert [record.record_id for record in bundle.manifest.records] == [
        "nz:amendments/2026/redirected-1#source_text",
        "nz:commencement/2026/9#source_text",
        "nz:regulations/2026/14#obligation",
        "nz:repeals/2026/4#source_text",
        "nz:statutes/2026/1#obligation",
    ]
    assert bundle.bridge_records[0].review_status == "deferred"
    assert bundle.bridge_records[0].known_gap_ids == ("track76-gap-redirected-amendment",)
    assert bundle.bridge_records[-1].review_status == "unreviewed"
    assert bundle.bridge_records[-1].known_gap_ids == ()
    assert all(record.family == bundle.manifest.records[0].family for record in bundle.manifest.records)
    assert bundle.manifest.records[4].attributes["rulespec_id"] == "nz:statutes/2026/1#obligation"


def test_batch_rac_candidate_bundle_from_extraction_manifest_round_trips_bundle() -> None:
    """Extraction-manifest inputs should preserve candidate ordering and bridge IDs."""
    source_bundle = build_rules_as_code_candidate_bundle_from_source_inventory()
    bundle = build_rules_as_code_candidate_bundle_from_extraction_manifest(source_bundle.manifest)

    assert [record.record_id for record in bundle.manifest.records] == [
        record.record_id for record in source_bundle.manifest.records
    ]
    assert [record["@id"] for record in [bridge.to_jsonld() for bridge in bundle.bridge_records]] == [
        bridge["@id"] for bridge in [record.to_jsonld() for record in source_bundle.bridge_records]
    ]


def test_export_rac_candidates_cli_writes_manifest_and_bridges(tmp_path: Path) -> None:
    """The batch CLI should emit manifest and bridge artifacts from the fixture inventory."""
    output_dir = tmp_path / "rac-batch"
    rc = main([
        "export-rac-candidates",
        "--output-dir",
        str(output_dir),
    ])

    manifest_path = output_dir / "rules_as_code_candidates.json"
    bridges_path = output_dir / "rules_as_code_bridges.json"
    summary_path = output_dir / "rules_as_code_candidates.md"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    bridges = json.loads(bridges_path.read_text(encoding="utf-8"))

    assert rc == 0
    assert manifest_path.is_file()
    assert bridges_path.is_file()
    assert summary_path.is_file()
    assert payload["summary"]["total_records"] == 5
    assert len(bridges) == 5
    assert bridges[0]["review_status"] == "deferred"
