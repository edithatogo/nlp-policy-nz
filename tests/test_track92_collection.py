from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.validate_track92_collection import validate

ROOT = Path(__file__).resolve().parents[1]


def inventory() -> dict:
    return json.loads((ROOT / "data/track92/source_inventory.json").read_text(encoding="utf-8"))


def contract(name: str) -> dict:
    return json.loads((ROOT / "data/track92" / name).read_text(encoding="utf-8"))


def test_checked_in_inventory_is_valid_but_fail_closed() -> None:
    value = inventory()
    assert validate(value) == []
    assert value["promotion"]["decision"] == "no-promotion"
    assert value["candidate_only"] is True


def test_missing_repository_role_fails_closed() -> None:
    value = inventory()
    value["repositories"] = copy.deepcopy(value["repositories"])
    del value["repositories"][0]["role"]
    assert any("repositories[0].role" in error for error in validate(value))


def test_unpinned_repository_fails_closed() -> None:
    value = inventory()
    value["repositories"][0]["revision"] = None
    assert any("revision" in error for error in validate(value))


def test_real_evidence_cannot_be_claimed_without_gate_data() -> None:
    value = inventory()
    value["promotion"]["decision"] = "promote"
    assert any("no-promotion" in error for error in validate(value))


def test_metadata_candidate_requires_immutable_hash_and_stays_unapproved() -> None:
    value = inventory()
    package = value["evidence_packages"][0]
    assert package["status"] == "metadata-only-candidate"
    assert len(package["source_sha256"]) == 64
    package["source_sha256"] = "invalid"
    assert any("source_sha256" in error for error in validate(value))


def test_empty_blocker_list_fails_closed() -> None:
    value = inventory()
    value["promotion"]["blockers"] = []
    assert any("promotion.blockers" in error for error in validate(value))


def test_concept_and_feedback_contracts_are_candidate_only() -> None:
    concept = contract("concept_pack_contract.json")
    feedback = contract("feedback_contract.json")
    assert concept["status"] == "candidate"
    assert concept["promotion"] == "no-promotion"
    assert feedback["candidate_only"] is True


def test_jurisdiction_manifest_registers_four_candidate_source_families() -> None:
    manifest = contract("jurisdiction_source_manifest.json")
    assert {item["source_family"] for item in manifest["jurisdictions"]} == {
        "legislation",
        "gazette",
        "guidance",
        "foi_cases",
    }
    assert manifest["promotion"] == "no-promotion"


def test_upstream_evidence_register_preserves_known_counts_and_limitations() -> None:
    register = contract("upstream_evidence_register.json")
    hathi = next(item for item in register["artifacts"] if item["repository"] == "edithatogo/hathi-nz")
    assert hathi["enumerated_count"] + hathi["pending_count"] == hathi["expected_count"]
    assert register["decision"] == "no-promotion"
    assert all(item["revision"] for item in register["artifacts"])
