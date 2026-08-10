"""Track 98 AU-NSW remote-contract gate tests."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_remote_contract_is_pinned_and_fail_closed():
    gate = json.loads((ROOT / "data/track98/au_nsw_remote_gate.json").read_text(encoding="utf-8"))

    assert gate["source_repository"] == "edithatogo/fyi-archive"
    assert len(gate["source_revision"]) == 40
    assert gate["capture_authorized"] is False
    assert gate["publication_authorized"] is False
    assert "rights-cleared" in gate["required_gate"]
