"""Tests for Track 31 New Zealand data-driven ontology induction."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import SKOS

from nlp_policy_nz.ontology.nz_ontologies import (
    NZ_ONTOLOGY_JSONLD_FILENAME,
    NZ_ONTOLOGY_MANIFEST_FILENAME,
    NZ_ONTOLOGY_SKOS_FILENAME,
    NZ_ONTOLOGY_TURTLE_FILENAME,
    build_nz_ontology_bundle,
    build_nz_ontology_graph,
    build_skos_concept_schemes,
    validate_nz_ontology_bundle,
    write_nz_ontology_artifacts,
)


def test_nz_ontology_bundle_covers_required_application_areas() -> None:
    """Track 31 should emit candidates for the planned NZ application areas."""
    bundle = build_nz_ontology_bundle()
    areas = {concept.application_area for concept in bundle.concepts}

    assert areas == {
        "act_structure",
        "hansard_debate_topics",
        "court_hierarchy",
        "maori_legal_concepts",
        "government_agencies",
    }
    assert bundle.summary["concept_count"] == len(bundle.concepts)
    assert bundle.summary["controlled_vocabulary_count"] == len(bundle.controlled_vocabularies)
    assert validate_nz_ontology_bundle(bundle) == []


def test_track31_builders_are_discoverable_from_top_level_package() -> None:
    """Track 31 helpers should be discoverable through the root package."""
    import nlp_policy_nz  # noqa: PLC0415

    assert nlp_policy_nz.build_nz_ontology_bundle is build_nz_ontology_bundle
    assert nlp_policy_nz.write_nz_ontology_artifacts is write_nz_ontology_artifacts


def test_nz_ontology_concepts_are_traceable_and_review_bounded() -> None:
    """Every induced concept should carry corpus evidence, anchors, and confidence."""
    bundle = build_nz_ontology_bundle()

    for concept in bundle.concepts:
        assert concept.uri.startswith("https://legal-nz.example.org/ontology/nz/")
        assert concept.evidence
        assert concept.ontology_anchors
        assert 0 < concept.confidence <= 1
        if concept.authority == "induced_nz":
            assert concept.review_status == "needs_review"

    authorities = {concept.authority for concept in bundle.concepts}
    assert authorities == {"authoritative_external", "induced_nz"}
    assert all(
        concept.review_status == "needs_review"
        for concept in bundle.concepts
        if concept.authority == "induced_nz"
    )
    assert [
        concept.review_status
        for concept in bundle.concepts
        if concept.authority == "authoritative_external"
    ] == ["approved"]
    act = next(concept for concept in bundle.concepts if concept.concept_id == "NZActOntology")
    assert "sioc-post-to-akn-debate" not in {
        anchor.mapping_id for anchor in act.ontology_anchors
    }


def test_nz_ontology_validation_reports_duplicate_labels_and_broken_hierarchies() -> None:
    """Bundle validation should catch non-unique labels and invalid hierarchy links."""
    bundle = build_nz_ontology_bundle()
    concepts_by_id = {concept.concept_id: concept for concept in bundle.concepts}
    duplicate_label = replace(
        concepts_by_id["NZProvision"],
        label=concepts_by_id["NZActOntology"].label,
    )
    missing_parent = replace(concepts_by_id["NZHansardOntology"], broader=("missing-parent",))
    broken_bundle = replace(
        bundle,
        concepts=tuple(
            duplicate_label
            if concept.concept_id == duplicate_label.concept_id
            else missing_parent
            if concept.concept_id == missing_parent.concept_id
            else concept
            for concept in bundle.concepts
        ),
    )

    errors = validate_nz_ontology_bundle(broken_bundle)

    assert "concept labels must be unique" in errors
    assert "NZHansardOntology has unknown broader concept missing-parent" in errors


def test_nz_ontology_validation_reports_hierarchy_cycles() -> None:
    """Bundle validation should catch cycles in concept broader relationships."""
    bundle = build_nz_ontology_bundle()
    concepts_by_id = {concept.concept_id: concept for concept in bundle.concepts}
    act = replace(concepts_by_id["NZActOntology"], broader=("NZProvision",))
    provision = replace(concepts_by_id["NZProvision"], broader=("NZActOntology",))
    cyclic_bundle = replace(
        bundle,
        concepts=tuple(
            act
            if concept.concept_id == act.concept_id
            else provision
            if concept.concept_id == provision.concept_id
            else concept
            for concept in bundle.concepts
        ),
    )

    errors = validate_nz_ontology_bundle(cyclic_bundle)

    assert "cycle detected: NZActOntology -> NZProvision -> NZActOntology" in errors


def test_skos_concept_schemes_have_unique_labels_and_expected_vocabularies() -> None:
    """Controlled vocabularies should be deterministic SKOS-ready schemes."""
    schemes = build_skos_concept_schemes()
    scheme_ids = {scheme.scheme_id for scheme in schemes}

    assert scheme_ids == {
        "nz-act-types",
        "hansard-topics",
        "court-levels",
        "government-agencies",
        "maori-legal-concepts",
    }
    for scheme in schemes:
        labels = [concept.pref_label for concept in scheme.concepts]
        assert labels == sorted(labels, key=str.casefold)
        assert len(labels) == len(set(labels))


def test_nz_ontology_graph_exports_rdf_with_stable_nodes() -> None:
    """Ontology candidates should export as parseable RDF without live services."""
    graph = build_nz_ontology_graph()
    turtle = graph.serialize(format="turtle")
    jsonld = graph.serialize(format="json-ld")
    parsed = Graph()
    parsed.parse(data=turtle, format="turtle")

    assert len(parsed) == len(graph)
    assert "NZActOntology" in turtle
    assert "NZHansardOntology" in turtle
    assert "Tikanga" in jsonld


def test_nz_ontology_graph_preserves_anchor_mapping_predicates() -> None:
    """RDF export should preserve Track 29 mapping predicate semantics."""
    graph = build_nz_ontology_graph()

    assert (
        URIRef("https://legal-nz.example.org/ontology/nz/NZHansardOntology"),
        SKOS.closeMatch,
        URIRef("https://legal-nz.example.org/ontology/nz/anchor/sioc/post"),
    ) in graph
    assert (
        URIRef("https://legal-nz.example.org/ontology/nz/NZActOntology"),
        SKOS.relatedMatch,
        URIRef("https://legal-nz.example.org/ontology/nz/anchor/eli/legalresource"),
    ) in graph


def test_nz_ontology_artifact_writer_round_trips(tmp_path: Path) -> None:
    """Writer should create JSON, RDF, and SKOS artifacts from the same bundle."""
    written = write_nz_ontology_artifacts(tmp_path)

    assert set(written) == {
        NZ_ONTOLOGY_MANIFEST_FILENAME,
        NZ_ONTOLOGY_TURTLE_FILENAME,
        NZ_ONTOLOGY_JSONLD_FILENAME,
        NZ_ONTOLOGY_SKOS_FILENAME,
    }

    manifest = json.loads(written[NZ_ONTOLOGY_MANIFEST_FILENAME].read_text(encoding="utf-8"))
    skos = json.loads(written[NZ_ONTOLOGY_SKOS_FILENAME].read_text(encoding="utf-8"))
    parsed = Graph()
    parsed.parse(written[NZ_ONTOLOGY_TURTLE_FILENAME], format="turtle")

    assert manifest["track_id"] == "track31_nz_data_driven_ontologies_20260625"
    assert manifest["summary"]["validation_errors"] == []
    assert skos["scheme_count"] == 5
    assert len(parsed) > manifest["summary"]["concept_count"]


def test_checked_in_nz_ontology_artifacts_match_writer(tmp_path: Path) -> None:
    """Checked-in Track 31 artifacts should stay in sync with the writer."""
    written = write_nz_ontology_artifacts(tmp_path)
    artifact_dir = Path("data/ontologies")

    for filename in (NZ_ONTOLOGY_MANIFEST_FILENAME, NZ_ONTOLOGY_SKOS_FILENAME):
        checked_in = json.loads((artifact_dir / filename).read_text(encoding="utf-8"))
        generated = json.loads(written[filename].read_text(encoding="utf-8"))
        assert checked_in == generated

    for filename, rdf_format in (
        (NZ_ONTOLOGY_TURTLE_FILENAME, "turtle"),
        (NZ_ONTOLOGY_JSONLD_FILENAME, "json-ld"),
    ):
        checked_in_graph = Graph()
        generated_graph = Graph()
        checked_in_graph.parse(artifact_dir / filename, format=rdf_format)
        generated_graph.parse(written[filename], format=rdf_format)
        assert set(checked_in_graph) == set(generated_graph)
