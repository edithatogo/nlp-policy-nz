from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.validate_track92_contracts import (
    validate,
    validate_concept_contract,
    validate_jurisdiction_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/track92"


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def test_checked_in_candidate_contracts_validate() -> None:
    assert validate(DATA) == []


def test_concept_contract_cannot_drop_a_promotion_gate() -> None:
    value = copy.deepcopy(load("concept_pack_contract.json"))
    value["promotion_requirements"].remove("rights")
    assert any("promotion_requirements" in error for error in validate_concept_contract(value))


def test_empty_jurisdiction_manifest_requires_blockers() -> None:
    value = copy.deepcopy(load("jurisdiction_source_manifest.json"))
    value["blockers"] = []
    assert any("blockers" in error for error in validate_jurisdiction_manifest(value))


def test_registered_jurisdiction_requires_every_source_field() -> None:
    value = copy.deepcopy(load("jurisdiction_source_manifest.json"))
    value["jurisdictions"] = [{"jurisdiction": "NZ"}]
    errors = validate_jurisdiction_manifest(value)
    assert any("missing" in error for error in errors)
