from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.ontology.registry import (
    TRACK26_MANIFEST_FILENAME,
    TRACK26_MANIFEST_PATH,
    build_track26_standards_manifest,
    build_track26_standards_registry,
    write_track26_standards_manifest,
)

EXPECTED_STANDARDS = (
    "CEN MetaLex",
    "DCAT",
    "DCAT-AP",
    "ECLI",
    "ELI",
    "ELI-DL",
    "EuroVoc",
    "LKIF",
    "LegalRuleML",
    "LexML",
    "OpenFisca",
    "PolicyEngine",
    "Popolo",
    "SKOS",
    "USLM",
    "W3C ORG",
    "formal OpenFisca/PolicyEngine variable/parameter/entity ontology",
    "full LKIF",
    "full LegalRuleML",
    "schema.org/Legislation",
)


def test_track26_registry_covers_the_requested_standards() -> None:
    registry = build_track26_standards_registry()
    standards = tuple(row["standard"] for row in registry)

    assert standards == EXPECTED_STANDARDS
    assert len(registry) == len(EXPECTED_STANDARDS)
    assert registry[0]["standard"] == "CEN MetaLex"
    assert registry[-1]["standard"] == "schema.org/Legislation"
    assert all(row["source_url"] for row in registry)
    assert all(row["source_license"] for row in registry)
    assert all(row["local_representation_paths"] for row in registry)


def test_track26_manifest_is_deterministic_and_json_serializable() -> None:
    manifest = build_track26_standards_manifest()
    rebuilt = build_track26_standards_manifest()

    assert manifest == rebuilt
    assert manifest["summary"]["entry_count"] == len(EXPECTED_STANDARDS)
    assert manifest["summary"]["license_assumption_count"] >= 1
    assert manifest["license_assumptions"]
    assert json.loads(json.dumps(manifest))


def test_track26_writer_matches_the_checked_in_manifest(tmp_path: Path) -> None:
    written_path = write_track26_standards_manifest(tmp_path / TRACK26_MANIFEST_FILENAME)
    repo_manifest_path = Path(TRACK26_MANIFEST_PATH)

    assert written_path.exists()
    assert json.loads(written_path.read_text(encoding="utf-8")) == build_track26_standards_manifest()
    assert json.loads(repo_manifest_path.read_text(encoding="utf-8")) == build_track26_standards_manifest()
