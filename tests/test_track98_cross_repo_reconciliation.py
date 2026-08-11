"""Track 98 cross-repository evidence remains fail-closed at capture."""

import json
from pathlib import Path


def test_approved_candidate_does_not_authorize_archive_capture() -> None:
    payload = json.loads(
        Path("data/track98/au_nsw_external_gate_reconciliation.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["candidate_artifact"]["records"] == 179
    assert len(payload["candidate_artifact"]["sha256"]) == 64
    assert payload["fyi_archive"]["capture_authorized"] is False
    assert payload["fyi_archive"]["publication_authorized"] is False
    assert payload["fyi_archive"]["time_window"] == "pending_human_approval"
