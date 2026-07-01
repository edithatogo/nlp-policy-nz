"""Tests for Track 30 ontology mapping inference."""

from __future__ import annotations

import json

from nlp_policy_nz.ontology.mapping_inference import (
    OntologyTerm,
    infer_embedding_matches,
    infer_exact_matches,
    infer_fuzzy_matches,
    infer_mapping_candidates,
    infer_structural_matches,
    infer_synonym_matches,
    llm_interpretation_prompt_schema,
    normalize_mapping_text,
    write_inferred_mapping_manifest,
    write_llm_interpretation_prompt,
)


def test_normalize_mapping_text_collapses_case_punctuation_and_spacing() -> None:
    """Normalized matching should be deterministic across punctuation noise."""
    assert normalize_mapping_text("  Legal-Effect: Obligation! ") == "legal effect obligation"


def test_exact_matches_use_normalized_aliases_without_false_positive_substrings() -> None:
    """Exact matching must not align terms just because one label contains another."""
    source_terms = (
        OntologyTerm("A", "court", "Court"),
        OntologyTerm("A", "obligation", "Legal obligation"),
    )
    target_terms = (
        OntologyTerm("B", "courthouse", "Courthouse"),
        OntologyTerm("B", "duty", "Duty", synonyms=("Legal obligation",)),
    )

    candidates = infer_exact_matches(source_terms, target_terms)

    assert [(candidate.source.term_id, candidate.target.term_id) for candidate in candidates] == [
        ("obligation", "duty")
    ]
    assert candidates[0].review_status == "needs_review"
    assert candidates[0].inferred is True


def test_fuzzy_matches_respect_threshold() -> None:
    """Fuzzy matching should accept near labels and reject distant labels."""
    source_terms = (OntologyTerm("LKIF", "prohibition", "Prohibition"),)
    target_terms = (
        OntologyTerm("ODRL", "prohibit", "Prohibit"),
        OntologyTerm("AKN", "debate", "Debate speech"),
    )

    candidates = infer_fuzzy_matches(source_terms, target_terms, threshold=0.8)

    assert [(candidate.target.standard, candidate.target.term_id) for candidate in candidates] == [
        ("ODRL", "prohibit")
    ]
    assert candidates[0].mapping_predicate == "skos:closeMatch"


def test_synonym_and_structural_evidence_are_reviewable() -> None:
    """Synonym and structural signals should carry auditable evidence strings."""
    source_terms = (
        OntologyTerm(
            "LKIF",
            "power",
            "Legal power",
            synonyms=("authority",),
            parents=("legal effect",),
            children=("delegated power",),
        ),
    )
    target_terms = (
        OntologyTerm(
            "Akoma Ntoso",
            "competence",
            "Competence",
            synonyms=("authority",),
            parents=("legal effect",),
            children=("delegated competence",),
        ),
    )

    synonym = infer_synonym_matches(
        source_terms,
        target_terms,
        synonym_groups=(("power", "authority", "competence"),),
    )
    structural = infer_structural_matches(source_terms, target_terms, threshold=0.3)

    assert synonym[0].methods == ("synonym",)
    assert "shared synonym group" in synonym[0].evidence[0]
    assert structural[0].methods == ("structural",)
    assert "structural neighbourhood" in structural[0].evidence[0]


def test_embedding_matches_use_supplied_vectors_without_model_download() -> None:
    """Embedding inference should work from offline precomputed vectors."""
    source_terms = (
        OntologyTerm("LKIF", "obligation", "Obligation", definition="A required legal act."),
    )
    target_terms = (
        OntologyTerm("LegalRuleML", "duty", "Duty", definition="A required normative act."),
        OntologyTerm("SIOC", "post", "Post", definition="A discourse message."),
    )
    source_vectors = {source_terms[0].key: (1.0, 0.0, 0.0)}
    target_vectors = {
        target_terms[0].key: (0.95, 0.05, 0.0),
        target_terms[1].key: (0.0, 1.0, 0.0),
    }

    candidates = infer_embedding_matches(
        source_terms,
        target_terms,
        source_vectors=source_vectors,
        target_vectors=target_vectors,
        threshold=0.9,
    )

    assert [(candidate.target.standard, candidate.target.term_id) for candidate in candidates] == [
        ("LegalRuleML", "duty")
    ]
    assert candidates[0].methods == ("embedding",)
    assert candidates[0].review_status == "needs_review"


def test_embedding_matches_can_use_injected_text_encoder() -> None:
    """Production can plug in the semantic layer while tests stay offline."""
    source_terms = (OntologyTerm("A", "permission", "Permission", definition="Allowed action"),)
    target_terms = (OntologyTerm("B", "permit", "Permit", definition="Authorized behaviour"),)

    def embed_texts(texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        return tuple(
            (1.0, 1.0) if "Permission" in text or "Authorized behaviour" in text else (0.0, 1.0)
            for text in texts
        )

    candidates = infer_mapping_candidates(
        source_terms,
        target_terms,
        embed_texts=embed_texts,
        fuzzy_threshold=0.99,
        structural_threshold=1.0,
        embedding_threshold=0.99,
    )

    assert candidates[0].methods == ("embedding",)
    assert "embedding cosine similarity" in candidates[0].evidence[0]


def test_merged_candidates_export_to_track29_mapping_record() -> None:
    """Merged inference output should feed Track 29 as a non-authoritative edge."""
    source_terms = (OntologyTerm("LKIF", "permission", "Permission", parents=("legal effect",)),)
    target_terms = (
        OntologyTerm("ODRL", "permission", "Permission", parents=("policy rule", "legal effect")),
    )

    candidates = infer_mapping_candidates(
        source_terms,
        target_terms,
        synonym_groups=(("permission", "allowance"),),
        structural_threshold=0.4,
    )
    record = candidates[0].to_mapping_record("tests/test_track30_mapping_inference.py")

    assert candidates[0].methods == ("exact", "synonym", "fuzzy", "structural")
    assert candidates[0].confidence > 0.95
    assert record.review_status == "needs_review"
    assert record.method == "inferred:exact,synonym,fuzzy,structural"
    assert record.notes.endswith("inferred=true")


def test_manifest_and_llm_prompt_round_trip(tmp_path) -> None:
    """Inference artifacts should be offline JSON files with review boundaries."""
    source_terms = (OntologyTerm("FOAF", "Person", "Person"),)
    target_terms = (OntologyTerm("schema.org", "Person", "Person"),)
    candidates = infer_mapping_candidates(source_terms, target_terms)

    manifest_path = write_inferred_mapping_manifest(candidates, tmp_path / "candidates.json")
    prompt_path = write_llm_interpretation_prompt(tmp_path / "prompt.json")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    prompt = json.loads(prompt_path.read_text(encoding="utf-8"))
    schema = llm_interpretation_prompt_schema()

    assert manifest["candidate_count"] == 1
    assert manifest["candidates"][0]["review_status"] == "needs_review"
    assert manifest["candidates"][0]["inferred"] is True
    assert prompt["task"] == "ontology_mapping_interpretation"
    assert prompt["required_output_schema"] == schema
    assert schema["properties"]["review_status"]["const"] == "needs_review"
