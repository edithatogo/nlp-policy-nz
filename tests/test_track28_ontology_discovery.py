from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.quality.track28_ontology_discovery import (
    BLOCKERS_FILENAME,
    DISCOVERY_LOG_FILENAME,
    REGISTRY_ADDENDUM_FILENAME,
    TRIAGE_FILENAME,
    approved_registry_addendum,
    build_blockers,
    build_discovery_log,
    build_registry_addendum,
    build_triage,
    discovery_candidates,
    write_track28_discovery_artifacts,
)


def test_track28_discovery_log_covers_required_source_categories() -> None:
    log = build_discovery_log()
    candidates = discovery_candidates()
    categories = {candidate.category for candidate in candidates}
    decisions = {candidate.decision for candidate in candidates}

    assert log["track_id"] == "track28_ontology_discovery_intake_20260625"
    assert log["candidate_count"] == len(candidates)
    assert {
        "official_standard",
        "government_vocabulary",
        "legal_informatics",
        "rules_as_code",
        "graph_vector_publication",
    } <= categories
    assert {"implement", "map-only", "monitor", "reject"} <= decisions
    assert all(candidate.source_url.startswith("https://") for candidate in candidates)
    assert all(1 <= candidate.total_score <= 25 for candidate in candidates)


def test_track28_triage_ranks_and_counts_candidates() -> None:
    triage = build_triage()
    ranked = triage["ranked_candidates"]
    totals = [row["total_score"] for row in ranked]

    assert triage["decision_counts"]["implement"] >= 1
    assert triage["decision_counts"]["map-only"] >= 1
    assert triage["decision_counts"]["monitor"] >= 1
    assert triage["decision_counts"]["reject"] >= 1
    assert totals == sorted(totals, reverse=True)
    assert ranked[0]["total_score"] >= ranked[-1]["total_score"]


def test_track28_registry_addendum_uses_track26_registry_contract() -> None:
    entries = approved_registry_addendum()
    addendum = build_registry_addendum()

    assert addendum["extends_registry"] == "track26_standards_registry"
    assert addendum["summary"]["entry_count"] == len(entries)
    assert addendum["summary"]["new_standard_count"] >= 1
    assert any(entry.standard == "NZGLS" for entry in entries)
    assert any(entry.standard == "SHACL" for entry in entries)
    assert all(entry.source_url for entry in entries)
    assert all(entry.local_representation_paths for entry in entries)


def test_track28_blockers_are_non_rejected_and_have_valid_types() -> None:
    blockers = build_blockers()
    valid_types = set(blockers["valid_blocker_types"])

    assert blockers["blocker_count"] == len(blockers["blockers"])
    assert all(row["decision"] != "reject" for row in blockers["blockers"])
    assert all(row["blocker_type"] in valid_types for row in blockers["blockers"])
    assert any(row["standard"] == "NZGLS" for row in blockers["blockers"])


def test_track28_artifact_writer_is_deterministic(tmp_path: Path) -> None:
    written = write_track28_discovery_artifacts(tmp_path)

    assert set(written) == {
        DISCOVERY_LOG_FILENAME,
        TRIAGE_FILENAME,
        REGISTRY_ADDENDUM_FILENAME,
        BLOCKERS_FILENAME,
    }
    assert json.loads(written[DISCOVERY_LOG_FILENAME].read_text(encoding="utf-8")) == (
        build_discovery_log()
    )
    assert json.loads(written[TRIAGE_FILENAME].read_text(encoding="utf-8")) == build_triage()
    assert json.loads(written[REGISTRY_ADDENDUM_FILENAME].read_text(encoding="utf-8")) == (
        build_registry_addendum()
    )
    assert json.loads(written[BLOCKERS_FILENAME].read_text(encoding="utf-8")) == (
        build_blockers()
    )
