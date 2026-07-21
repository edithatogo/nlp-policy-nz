from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts.validate_nz_conformance_packet import validate

ROOT = Path(__file__).resolve().parents[1]


def packet() -> dict:
    return json.loads((ROOT / "data/foio/nz_conformance_packet.json").read_text(encoding="utf-8"))


def test_checked_in_packet_is_hash_pinned_and_fail_closed() -> None:
    value = packet()
    assert validate(value, ROOT) == []
    assert value["promotion"] == "no-promotion"


def test_packet_rejects_fixture_digest_drift() -> None:
    value = copy.deepcopy(packet())
    value["fixture"]["sha256"] = "0" * 64
    assert any("SHA-256" in error for error in validate(value, ROOT))
