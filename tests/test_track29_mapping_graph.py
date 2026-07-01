from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rdflib import Graph

from nlp_policy_nz.ontology.mapping_graph import (
    MAPPING_JSONLD_FILENAME,
    MAPPING_MANIFEST_FILENAME,
    MAPPING_MERMAID_FILENAME,
    MAPPING_SCHEMA_FILENAME,
    MAPPING_SUMMARY_FILENAME,
    MAPPING_TURTLE_FILENAME,
    SEED_MAPPINGS,
    OntologyMappingRecord,
    add_mapping_record,
    build_mapping_graph,
    build_mapping_manifest,
    get_equivalent,
    load_mapping_manifest,
    mapping_json_schema,
    mapping_summary,
    mappings_by_standard_pair,
    remove_mapping_record,
    render_mermaid_graph,
    replace_mapping_record,
    traverse_mappings,
    update_mapping_review_status,
    validate_mapping_manifest,
    write_mapping_artifacts,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_mapping_record_validation_and_manifest_contract() -> None:
    manifest = build_mapping_manifest()
    records = validate_mapping_manifest(manifest)
    schema = mapping_json_schema()

    assert records == tuple(sorted(SEED_MAPPINGS, key=lambda record: record.mapping_id))
    assert manifest["summary"]["mapping_count"] == len(SEED_MAPPINGS)
    assert "skos:closeMatch" in manifest["mapping_predicates"]
    assert "approved" in manifest["review_statuses"]
    assert set(schema["required"]) <= set(manifest)


def test_mapping_record_rejects_invalid_confidence() -> None:
    payload = SEED_MAPPINGS[0].to_dict()
    payload["confidence"] = 2

    try:
        OntologyMappingRecord.from_dict(payload)
    except ValueError as exc:
        assert "confidence" in str(exc)
    else:  # pragma: no cover - defensive assertion branch
        raise AssertionError("invalid confidence was accepted")


def test_mapping_record_crud_helpers_are_immutable() -> None:
    record = OntologyMappingRecord(
        mapping_id="test-dcat-to-skos",
        source_standard="DCAT",
        target_standard="SKOS",
        source_term="theme",
        target_term="Concept",
        mapping_predicate="skos:relatedMatch",
        confidence=0.64,
        method="test fixture",
        provenance="tests/test_track29_mapping_graph.py",
        review_status="needs_review",
    )

    added = add_mapping_record(SEED_MAPPINGS, record)
    approved = update_mapping_review_status(added, record.mapping_id, "approved")
    replaced = replace_mapping_record(
        approved,
        OntologyMappingRecord.from_dict(
            {
                **record.to_dict(),
                "confidence": 0.7,
                "review_status": "approved",
            }
        ),
    )
    removed = remove_mapping_record(replaced, record.mapping_id)

    assert len(added) == len(SEED_MAPPINGS) + 1
    assert len(SEED_MAPPINGS) == 12
    assert get_equivalent("theme", "DCAT", "SKOS", mappings=approved) == ()
    assert any(item.confidence == 0.7 for item in replaced)
    assert removed == tuple(sorted(SEED_MAPPINGS, key=lambda item: item.mapping_id))


def test_mapping_record_crud_helpers_reject_duplicate_or_missing_ids() -> None:
    duplicate = SEED_MAPPINGS[0]
    missing = OntologyMappingRecord.from_dict(
        {**duplicate.to_dict(), "mapping_id": "missing-mapping-id"}
    )

    for action in (
        lambda: add_mapping_record(SEED_MAPPINGS, duplicate),
        lambda: replace_mapping_record(SEED_MAPPINGS, missing),
        lambda: remove_mapping_record(SEED_MAPPINGS, "missing-mapping-id"),
        lambda: update_mapping_review_status(
            SEED_MAPPINGS,
            "missing-mapping-id",
            "approved",
        ),
    ):
        try:
            action()
        except ValueError as exc:
            assert "mapping_id" in str(exc)
        else:  # pragma: no cover - defensive assertion branch
            raise AssertionError("invalid CRUD operation was accepted")


def test_mapping_queries_resolve_equivalents_and_traversals() -> None:
    people = get_equivalent("Person", "FOAF", "schema.org")
    lkif_paths = traverse_mappings("Permission", "LKIF", max_hops=2)
    dcat_to_nz = mappings_by_standard_pair("DCAT", "NZGLS")

    assert people == ("Person",)
    assert any(path["target"] == "ODRL::Permission" for path in lkif_paths)
    assert len(dcat_to_nz) == 1
    assert dcat_to_nz[0].mapping_predicate == "source:crosswalk"


def test_mapping_graph_exports_rdf_and_mermaid() -> None:
    graph = build_mapping_graph()
    turtle = graph.serialize(format="turtle")
    jsonld = graph.serialize(format="json-ld")
    mermaid = render_mermaid_graph()

    parsed = Graph()
    parsed.parse(data=turtle, format="turtle")

    assert len(graph) >= len(SEED_MAPPINGS) * 10
    assert len(parsed) == len(graph)
    assert "foaf-person-to-schema-person" in turtle
    assert "foaf-person-to-schema-person" in jsonld
    assert mermaid.startswith("graph LR")
    assert "FOAF" in mermaid


def test_mapping_artifact_writer_round_trips(tmp_path: Path) -> None:
    written = write_mapping_artifacts(tmp_path)

    assert set(written) == {
        MAPPING_MANIFEST_FILENAME,
        MAPPING_SCHEMA_FILENAME,
        MAPPING_TURTLE_FILENAME,
        MAPPING_JSONLD_FILENAME,
        MAPPING_SUMMARY_FILENAME,
        MAPPING_MERMAID_FILENAME,
    }
    records = load_mapping_manifest(written[MAPPING_MANIFEST_FILENAME])
    summary = json.loads(written[MAPPING_SUMMARY_FILENAME].read_text(encoding="utf-8"))

    assert records == tuple(sorted(SEED_MAPPINGS, key=lambda record: record.mapping_id))
    assert summary == mapping_summary(SEED_MAPPINGS)
    assert written[MAPPING_TURTLE_FILENAME].read_text(encoding="utf-8").strip()
    assert written[MAPPING_JSONLD_FILENAME].read_text(encoding="utf-8").strip()
