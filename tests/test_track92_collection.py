from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.validate_track92_collection import validate

ROOT = Path(__file__).resolve().parents[1]


def inventory() -> dict:
    return json.loads((ROOT / "data/track92/source_inventory.json").read_text(encoding="utf-8"))


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


def test_real_evidence_cannot_be_claimed_without_gate_data() -> None:
    value = inventory()
    value["promotion"]["decision"] = "promote"
    assert any("no-promotion" in error for error in validate(value))

