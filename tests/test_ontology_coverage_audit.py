from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.quality.ontology_coverage_audit import (
    OUTPUT_FILENAMES,
    build_audit_bundle,
    build_blocker_register,
    build_coverage_matrix,
    build_evidence_markdown,
    build_prioritized_backlog,
    matrix_to_markdown,
    write_track25_artifacts,
)


def test_track25_matrix_captures_expected_standards() -> None:
    matrix = build_coverage_matrix()
    standards = {row["standard"] for row in matrix}

    assert len(matrix) == 18
    assert {
        "Akoma Ntoso / LegalDocML",
        "PROV-O",
        "FOAF / SIOC",
        "Wikidata / schema.org",
        "LKIF-inspired legal effects",
        "TimeML / OWL-Time",
        "LegalRuleML / Catala",
        "OpenFisca / PolicyEngine ontology",
        "ELI / ELI-DL",
        "ECLI",
        "EuroVoc / SKOS",
        "CEN MetaLex",
        "USLM",
        "LexML",
        "Popolo",
        "W3C ORG",
        "DCAT / DCAT-AP",
    }.issubset(standards)

    implemented = [row for row in matrix if row["coverage_status"] == "implemented"]
    missing = [row for row in matrix if row["coverage_status"] == "missing"]
    assert {row["standard"] for row in implemented} == {"PROV-O", "FOAF / SIOC"}
    assert {"ELI / ELI-DL", "ECLI", "EuroVoc / SKOS", "CEN MetaLex", "USLM", "LexML", "Popolo", "W3C ORG", "DCAT / DCAT-AP"}.issubset(
        {row["standard"] for row in missing}
    )


def test_blockers_and_backlog_are_json_serializable() -> None:
    bundle = build_audit_bundle()
    blockers = build_blocker_register(bundle.matrix)
    backlog = build_prioritized_backlog(bundle.matrix)

    assert blockers
    assert backlog
    assert json.loads(json.dumps(blockers))
    assert json.loads(json.dumps(backlog))
    assert backlog[0]["rank"] == 1
    assert backlog[0]["priority"] <= backlog[-1]["priority"]


def test_markdown_and_artifact_writer(tmp_path: Path) -> None:
    bundle = build_audit_bundle()
    markdown = build_evidence_markdown(bundle)

    assert markdown.startswith("# Track 25 Ontology Coverage Audit")
    assert "## Missing surfaces" in markdown
    assert "## Priority backlog" in markdown
    assert "| Standard | Status | Files | Blocker | Next action |" in matrix_to_markdown(
        bundle.matrix
    )

    written = write_track25_artifacts(tmp_path)
    assert set(written) == set(OUTPUT_FILENAMES.values())
    for path in written.values():
        assert path.exists()
        assert path.read_text(encoding="utf-8").strip()
