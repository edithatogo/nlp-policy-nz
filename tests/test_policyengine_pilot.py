"""Tests for the Track 79 PolicyEngine pilot package generator."""

from __future__ import annotations

import importlib
import json
import sys
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

import pytest

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.policyengine_pilot import (
    build_policyengine_pilot_package,
    load_policyengine_pilot_domain_json,
    render_policyengine_pilot_oracles_json,
    write_policyengine_pilot_package,
)
from nlp_policy_nz.rulespec_promotion import PromotionState

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "track79" / "policyengine_pilot_manifest.json"


@contextmanager
def _import_from_root(root: Path):
    root_str = str(root)
    sys.path.insert(0, root_str)
    try:
        yield
    finally:
        sys.path.remove(root_str)


def _clear_policyengine_modules() -> None:
    for module_name in list(sys.modules):
        if module_name == "policyengine_nz_commencement_pilot" or module_name.startswith(
            "policyengine_nz_commencement_pilot."
        ):
            del sys.modules[module_name]


def test_policyengine_pilot_manifest_loads_reviewed_domain() -> None:
    """The pilot manifest should load a reviewed commencement domain."""
    domain = load_policyengine_pilot_domain_json(MANIFEST)

    assert domain.review_state.value == "promoted"
    assert domain.package_name == "policyengine_nz_commencement_pilot"
    assert domain.source_excerpt == "This Act commences on the day after Royal assent."
    assert len(domain.oracle_cases) == 3


def test_policyengine_pilot_package_writes_and_executes_oracles(tmp_path: Path) -> None:
    """The generated package should write files and execute oracle fixtures."""
    domain = load_policyengine_pilot_domain_json(MANIFEST)
    package = build_policyengine_pilot_package(domain)
    output_dir = write_policyengine_pilot_package(package, tmp_path / "pilot")

    variable_module = output_dir / "policyengine_nz_commencement_pilot" / "variables" / "commencement.py"
    oracle_path = output_dir / "policyengine_nz_commencement_pilot" / "oracle_fixtures.json"
    evaluation_path = output_dir / "policyengine_nz_commencement_pilot" / "evaluate_oracles.py"

    assert variable_module.is_file()
    assert oracle_path.is_file()
    assert evaluation_path.is_file()
    assert (output_dir / "rulespec_promotion_handoff.json").is_file()
    assert (output_dir / "rulespec_promotion_handoff.yaml").is_file()

    _clear_policyengine_modules()
    with _import_from_root(output_dir):
        generated = importlib.import_module("policyengine_nz_commencement_pilot.variables.commencement")
        formula = generated.ActCommenced()

        assert formula.evaluate(assessment_date="2026-06-30") is False
        assert formula.evaluate(assessment_date="2026-07-01") is True

        evaluator = importlib.import_module("policyengine_nz_commencement_pilot.evaluate_oracles")
        report = evaluator.run_oracles(oracle_path)

    assert report["passed"] is True
    assert len(report["results"]) == 3
    assert all(item["passed"] for item in report["results"])
    assert package.execution_report.passed is True


def test_policyengine_pilot_cli_writes_package(tmp_path: Path) -> None:
    """The CLI should build the pilot package from the checked-in manifest."""
    output_dir = tmp_path / "cli-pilot"

    rc = main(
        [
            "policyengine-pilot",
            "--manifest",
            str(MANIFEST),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert rc == 0
    metadata = json.loads((output_dir / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["execution_report"]["passed"] is True
    assert metadata["domain"]["package_name"] == "policyengine_nz_commencement_pilot"


def test_policyengine_pilot_oracle_json_is_stable() -> None:
    """Oracle fixtures should serialize deterministically for CI review."""
    domain = load_policyengine_pilot_domain_json(MANIFEST)
    payload = json.loads(render_policyengine_pilot_oracles_json(domain))

    assert payload["track_id"] == "track79_policyengine_executable_pilot_20260705"
    assert payload["cases"][1]["expected_output"] is True


def test_policyengine_pilot_rejects_hash_drift() -> None:
    """The builder should fail closed when the source checksum drifts."""
    domain = load_policyengine_pilot_domain_json(MANIFEST)

    with pytest.raises(ValueError, match="SHA-256"):
        build_policyengine_pilot_package(replace(domain, source_sha256="0" * 64))


def test_policyengine_pilot_rejects_unpromoted_domain() -> None:
    """The builder should refuse to generate packages for unpromoted domains."""
    domain = load_policyengine_pilot_domain_json(MANIFEST)

    with pytest.raises(ValueError, match="must be promoted"):
        build_policyengine_pilot_package(replace(domain, review_state=PromotionState.REVIEWED))
