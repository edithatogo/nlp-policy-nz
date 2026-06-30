from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.quality.track25_ontology_coverage import (
    TRACK25_ARTIFACT_DIR,
    TRACK25_AUDIT_FILENAME,
    TRACK25_BACKLOG_FILENAME,
    TRACK25_BLOCKER_REGISTER_FILENAME,
    build_blocker_register,
    build_coverage_matrix,
    build_prioritized_backlog,
    build_track25_ontology_coverage_audit,
    enumerate_ontology_facing_systems,
    repo_root,
    slugify_identifier,
    write_track25_ontology_coverage_artifacts,
)


def _row_index(rows: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    return {(row["system_key"], row["upstream_standard"]): row for row in rows}


def test_slugify_identifier_is_stable() -> None:
    assert slugify_identifier("LegalRuleML / Catala hooks") == "legalruleml_catala_hooks"
    assert slugify_identifier("  ") == "item"


def test_enumerate_ontology_facing_systems_covers_expected_repo_surfaces() -> None:
    systems = enumerate_ontology_facing_systems(repo_root())
    system_keys = [system["system_key"] for system in systems]

    assert system_keys == [
        "akn_legal_docml",
        "provenance",
        "linked_data_graphs",
        "knowledge_graph_exports",
        "legal_semantics",
        "temporal_semantics",
        "normative_emission",
        "rules_as_code_bridge",
    ]

    akn = systems[0]
    assert "src/nlp_policy_nz/schema/akn_v3.py" in akn["local_files"]
    assert "Akoma Ntoso" in [standard["upstream_standard"] for standard in akn["standards"]]
    assert akn["local_file_status"] in {"complete", "partial"}


def test_build_coverage_matrix_includes_implemented_and_missing_standards() -> None:
    rows = build_coverage_matrix(repo_root())
    index = _row_index(rows)

    assert index[("provenance", "PROV-O")]["coverage_status"] == "implemented"
    assert index[("linked_data_graphs", "FOAF")]["coverage_status"] == "implemented"
    assert index[("linked_data_graphs", "SIOC")]["coverage_status"] == "implemented"
    assert index[("akn_legal_docml", "Akoma Ntoso")]["coverage_status"] == "implemented"
    assert index[("akn_legal_docml", "LegalDocML")]["coverage_status"] == "implemented"
    assert index[("knowledge_graph_exports", "Wikidata")]["coverage_status"] == "partial"
    assert (
        index[("knowledge_graph_exports", "schema.org/Legislation")]["coverage_status"] == "missing"
    )
    assert index[("legal_semantics", "full LKIF")]["coverage_status"] == "missing"
    assert index[("normative_emission", "full LegalRuleML")]["coverage_status"] == "missing"
    assert (
        index[
            (
                "rules_as_code_bridge",
                "formal OpenFisca/PolicyEngine variable/parameter/entity ontology",
            )
        ]["coverage_status"]
        == "missing"
    )

    assert index[("akn_legal_docml", "ELI")]["blocker_type"] == "source_data"
    assert (
        index[("knowledge_graph_exports", "schema.org/Legislation")]["blocker_type"]
        == "specification"
    )

    json.dumps(rows)


def test_blocker_register_and_backlog_are_deterministic() -> None:
    blockers_first = build_blocker_register(repo_root())
    blockers_second = build_blocker_register(repo_root())
    backlog = build_prioritized_backlog(repo_root())

    assert blockers_first == blockers_second
    assert all(row["blocker_type"] != "none" for row in blockers_first)
    assert all(item["blocker_type"] != "none" for item in backlog)

    priorities = [item["priority"] for item in backlog]
    priority_ranks = {"p0": 0, "p1": 1, "p2": 2, "p3": 3}
    assert priorities == sorted(priorities, key=priority_ranks.__getitem__)


def test_audit_bundle_is_json_serializable_and_consistent() -> None:
    audit = build_track25_ontology_coverage_audit(repo_root())
    assert audit["summary"]["row_count"] == len(audit["coverage_matrix"])
    assert audit["summary"]["status_counts"]["implemented"] >= 3
    assert len(audit["coverage_matrix"]) > len(audit["systems"])

    json.dumps(audit)


def test_track25_writer_matches_checked_in_artifacts(tmp_path: Path) -> None:
    written = write_track25_ontology_coverage_artifacts(tmp_path)
    artifact_dir = Path(TRACK25_ARTIFACT_DIR)

    assert json.loads(written["coverage_manifest"].read_text(encoding="utf-8")) == json.loads(
        (artifact_dir / TRACK25_AUDIT_FILENAME).read_text(encoding="utf-8")
    )
    assert json.loads(written["data_blocker_register"].read_text(encoding="utf-8")) == json.loads(
        (artifact_dir / TRACK25_BLOCKER_REGISTER_FILENAME).read_text(encoding="utf-8")
    )
    assert json.loads(
        written["ontology_implementation_backlog"].read_text(encoding="utf-8")
    ) == json.loads((artifact_dir / TRACK25_BACKLOG_FILENAME).read_text(encoding="utf-8"))
