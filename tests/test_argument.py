"""Tests for Track 13 argument mining."""

from __future__ import annotations

import json

from nlp_policy_nz.discourse import (
    ArgumentDetector,
    ArgumentGraph,
    evaluate_argument_components,
    link_arguments_to_issues,
)
from nlp_policy_nz.storage import PipelineRecord, load_from_parquet, serialize_to_parquet


def test_argument_detector_identifies_premise_and_conclusion() -> None:
    """Argument detector should label premise and conclusion spans."""
    detector = ArgumentDetector()

    arguments = detector.detect(
        "Because rents are rising, families need support. Therefore the bill should pass."
    )

    by_type = {argument.component_type for argument in arguments}
    assert {"premise", "conclusion"} <= by_type
    assert arguments[0].start < arguments[0].end
    assert all(argument.confidence >= 0.8 for argument in arguments)


def test_argument_component_fixture_exceeds_f1_threshold() -> None:
    """Track 13 labelled component fixture should exceed the >80% F1 gate."""
    detector = ArgumentDetector()
    labelled = [
        {
            "text": "Because emissions are rising, the bill should pass.",
            "expected": ["premise", "conclusion"],
        },
        {
            "text": "Therefore this amendment should be rejected.",
            "expected": ["conclusion"],
        },
        {
            "text": "Members resumed after the dinner break.",
            "expected": ["none"],
        },
        {
            "text": "The evidence shows costs will fall. This supports the policy.",
            "expected": ["premise", "conclusion"],
        },
    ]

    score = evaluate_argument_components(labelled, detector=detector)

    assert score["f1"] >= 0.8


def test_argument_graph_exports_aif_jsonld() -> None:
    """Argument graph should expose support and attack relations as JSON-LD."""
    detector = ArgumentDetector()
    arguments = detector.detect(
        "Because costs will fall, the bill should pass. However the amendment would delay relief."
    )
    graph = ArgumentGraph.from_arguments(arguments, issue="housing affordability")

    payload = graph.to_aif_jsonld()

    assert payload["@context"]["aif"] == "http://www.arg.dundee.ac.uk/aif#"
    assert payload["issue"] == "housing affordability"
    assert any(edge["relation"] in {"support", "attack"} for edge in payload["edges"])
    json.dumps(payload)


def test_issue_argument_linking_uses_token_similarity() -> None:
    """Arguments should link to the most similar policy issue."""
    detector = ArgumentDetector()
    arguments = detector.detect("Because rents are rising, housing support should pass.")

    links = link_arguments_to_issues(arguments, ["housing support", "fisheries quota"])

    assert links[0]["issue"] == "housing support"
    similarity = links[0]["similarity"]
    assert isinstance(similarity, float)
    assert similarity > 0


def test_pipeline_record_roundtrips_arguments_and_stance(tmp_path) -> None:
    """PipelineRecord should preserve Track 13 discourse fields in Parquet."""
    detector = ArgumentDetector()
    arguments = [
        argument.to_dict() for argument in detector.detect("Therefore the bill should pass.")
    ]
    record = PipelineRecord(
        doc_id="argument-1",
        corpus_source="hansard",
        raw_text="Therefore the bill should pass.",
        cleaned_tokens=["Therefore", "the", "bill", "should", "pass"],
        nz_act_citations=[],
        te_reo_terms=[],
        arguments=arguments,
        argument_label_source="predicted",
        stance="pro",
        stance_label_source="predicted",
    )

    path = tmp_path / "arguments.parquet"
    serialize_to_parquet([record], path)
    loaded = load_from_parquet(path)

    assert loaded[0].arguments == arguments
    assert loaded[0].argument_label_source == "predicted"
    assert loaded[0].stance == "pro"
    assert loaded[0].stance_label_source == "predicted"
