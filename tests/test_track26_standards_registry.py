from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.ontology.registry import (
    BLOCKER_TYPES,
    IMPLEMENTATION_STATUSES,
    TRACK26_MANIFEST_FILENAME,
    TRACK26_MANIFEST_PATH,
    build_track26_standards_manifest,
    build_track26_standards_registry,
    write_track26_standards_manifest,
)
from nlp_policy_nz.ontology.standards import (
    ControlledConcept,
    LegislationProfile,
    build_eurovoc_concept,
    build_schema_legislation,
    load_controlled_concept,
    load_schema_legislation,
)

TRACK26_SCHEMA_PATH = Path("data/ontologies/standards_registry.schema.json")

EXPECTED_STANDARDS = (
    "CEN MetaLex",
    "DCAT",
    "DCAT-AP",
    "ECLI",
    "ELI",
    "ELI-DL",
    "EuroVoc",
    "formal OpenFisca/PolicyEngine variable/parameter/entity ontology",
    "full LegalRuleML",
    "full LKIF",
    "LegalRuleML",
    "LexML",
    "LKIF",
    "OpenFisca",
    "PolicyEngine",
    "Popolo",
    "schema.org/Legislation",
    "SKOS",
    "USLM",
    "W3C ORG",
)


def test_track26_registry_covers_the_requested_standards() -> None:
    registry = build_track26_standards_registry()
    standards = tuple(row["standard"] for row in registry)

    assert standards == EXPECTED_STANDARDS
    assert len(registry) == len(EXPECTED_STANDARDS)
    assert registry[0]["standard"] == "CEN MetaLex"
    assert registry[-1]["standard"] == "W3C ORG"
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
    assert (
        json.loads(written_path.read_text(encoding="utf-8")) == build_track26_standards_manifest()
    )
    assert (
        json.loads(repo_manifest_path.read_text(encoding="utf-8"))
        == build_track26_standards_manifest()
    )


def test_track26_schema_matches_manifest_contract() -> None:
    schema = json.loads(TRACK26_SCHEMA_PATH.read_text(encoding="utf-8"))
    manifest = build_track26_standards_manifest()

    required_root = set(schema["required"])
    required_entry = set(schema["properties"]["entries"]["items"]["required"])
    implementation_enum = tuple(
        schema["properties"]["entries"]["items"]["properties"]["implementation_status"]["enum"]
    )
    blocker_enum = tuple(
        schema["properties"]["entries"]["items"]["properties"]["blocker_type"]["enum"]
    )

    assert required_root <= set(manifest)
    assert required_entry <= set(manifest["entries"][0])
    assert implementation_enum == IMPLEMENTATION_STATUSES
    assert blocker_enum == BLOCKER_TYPES


def test_track26_controlled_concept_round_trip(tmp_path: Path) -> None:
    concept = ControlledConcept(
        scheme_id="eurovoc",
        concept_id="1234",
        pref_label="parliamentary procedure",
        notation="1234",
        broader=("procedure",),
    )
    payload = build_eurovoc_concept(concept)
    path = tmp_path / "concept.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_controlled_concept(path)

    assert loaded == concept


def test_track26_schema_legislation_round_trip(tmp_path: Path) -> None:
    profile = LegislationProfile(
        identifier="nz-2026-001",
        name="Example Act",
        jurisdiction="NZ",
        same_as=("https://example.org/act",),
    )
    payload = build_schema_legislation(profile)
    path = tmp_path / "legislation.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_schema_legislation(path)

    assert loaded == profile
