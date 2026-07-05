"""Tests for Track 80 multi-engine parity artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.ontology.multi_engine_parity import (
    build_multi_engine_parity_bundle,
    load_track80_domain_json,
    render_multi_engine_parity_report_json,
    write_multi_engine_parity_bundle,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "track79" / "policyengine_pilot_manifest.json"
TRACK80 = ROOT / "conductor" / "tracks" / "track80_openfisca_multi_engine_parity_20260705"


def test_track80_track_artifacts_exist() -> None:
    """Track 80 should ship its local spec, plan, metadata, and index files."""
    expected = [
        TRACK80 / "index.md",
        TRACK80 / "metadata.json",
        TRACK80 / "plan.md",
        TRACK80 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track80_bundle_writes_policyengine_and_openfisca_exports(tmp_path: Path) -> None:
    """Track 80 should export both package skeletons and a parity report."""
    domain = load_track80_domain_json(MANIFEST)
    bundle = build_multi_engine_parity_bundle(domain)
    output_dir = write_multi_engine_parity_bundle(bundle, tmp_path / "parity")

    policyengine_dir = output_dir / "policyengine" / bundle.policyengine_package.package_name
    openfisca_dir = output_dir / "openfisca" / bundle.openfisca_package.package_name
    report_json = output_dir / "multi_engine_parity_report.json"
    report_md = output_dir / "multi_engine_parity_report.md"

    assert policyengine_dir.is_dir()
    assert openfisca_dir.is_dir()
    assert (policyengine_dir / "variables" / "generated.py").is_file()
    assert (openfisca_dir / "variables" / "generated.py").is_file()
    assert report_json.is_file()
    assert report_md.is_file()

    report = json.loads(report_json.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["engine_contracts"][0]["support_level"] == "primary"
    assert report["engine_contracts"][1]["support_level"] == "export-only"
    assert report["cases"][0]["policyengine_output"] == report["cases"][0]["openfisca_output"]
    assert report["known_gaps"]


def test_track80_report_serializes_source_ids_and_versions() -> None:
    """The parity report should expose source IDs, engine versions, and outputs."""
    domain = load_track80_domain_json(MANIFEST)
    bundle = build_multi_engine_parity_bundle(domain)
    payload = json.loads(render_multi_engine_parity_report_json(bundle.report))

    assert payload["schema_version"] == "track80.multi-engine-parity.v1"
    assert payload["source_citation_path"] == "nz/statutes/commencement/2026/1"
    assert "reference" in payload["engine_contracts"][0]["runtime_version"]
    assert "reference" in payload["engine_contracts"][1]["runtime_version"]
    assert payload["cases"][0]["expected_output"] is False
    assert payload["cases"][1]["passed"] is True
    assert "record_id" not in payload


def test_track80_cli_writes_parity_bundle(tmp_path: Path) -> None:
    """The CLI should build the parity bundle from the reviewed manifest."""
    output_dir = tmp_path / "cli-parity"

    rc = main(
        [
            "multi-engine-parity",
            "--manifest",
            str(MANIFEST),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert rc == 0
    report = json.loads((output_dir / "multi_engine_parity_report.json").read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert (output_dir / "policyengine" / "policyengine_nz_commencement_pilot" / "variables" / "generated.py").is_file()
    assert (output_dir / "openfisca" / "openfisca_nz_commencement_pilot" / "variables" / "generated.py").is_file()
    assert (output_dir / "policyengine" / "README.md").is_file()
    assert (output_dir / "openfisca" / "README.md").is_file()
