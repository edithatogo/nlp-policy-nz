from __future__ import annotations

import json
from pathlib import Path

EVIDENCE = Path("data/track98/au_rollout_evidence.json")


def test_au_rollout_evidence_is_candidate_only_and_pinned() -> None:
    value = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert value["status"] == "candidate-discovery-only"
    assert value["candidate_only"] is True
    assert value["promotion"] == "no-promotion"
    assert len(value["source_revision"]) == 40
    assert value["source_worktree_status"] == "dirty-at-capture"
    assert value["source_uri"] == "https://www.righttoknow.org.au/"


def test_au_rollout_evidence_does_not_overstate_source_families() -> None:
    value = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert value["available_source_families"] == ["foi_cases"]
    assert set(value["missing_source_families"]) == {"legislation", "gazette", "guidance"}
    assert len(value["blockers"]) >= 3
