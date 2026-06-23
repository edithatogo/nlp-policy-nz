"""Tests for Track 13 API and graph integration."""

from __future__ import annotations

import json

from nlp_policy_nz.api.server import _record_to_dict
from nlp_policy_nz.cli.graph import export_argument_graph_jsonld
from nlp_policy_nz.storage import PipelineRecord


def test_api_record_dict_includes_arguments_and_stance() -> None:
    """API serialization should expose Track 13 discourse fields."""
    record = PipelineRecord(
        doc_id="inline-argument-1",
        corpus_source="hansard",
        raw_text="Therefore the bill should pass.",
        cleaned_tokens=["Therefore", "the", "bill", "should", "pass"],
        nz_act_citations=[],
        te_reo_terms=[],
        arguments=[{"component_id": "arg-1", "component_type": "conclusion"}],
        argument_label_source="predicted",
        stance="pro",
        stance_label_source="predicted",
    )

    payload = _record_to_dict(record)

    assert payload["arguments"] == record.arguments
    assert payload["argument_label_source"] == "predicted"
    assert payload["stance"] == "pro"
    assert payload["stance_label_source"] == "predicted"


def test_policy_graph_exports_record_arguments_as_aif_jsonld() -> None:
    """Graph module should expose an AIF JSON-LD export for record arguments."""
    record = PipelineRecord(
        doc_id="speech-1",
        corpus_source="hansard",
        raw_text="Because rents are rising, the bill should pass.",
        cleaned_tokens=["Because", "rents", "are", "rising"],
        nz_act_citations=[],
        te_reo_terms=[],
        arguments=[
            {
                "component_id": "arg-1-premise",
                "component_type": "premise",
                "text": "Because rents are rising",
                "start": 0,
                "end": 24,
                "confidence": 0.9,
            },
            {
                "component_id": "arg-1-conclusion",
                "component_type": "conclusion",
                "text": "the bill should pass",
                "start": 26,
                "end": 46,
                "confidence": 0.9,
            },
        ],
    )

    payload = export_argument_graph_jsonld([record], issue="housing")

    assert payload["@context"]["aif"] == "http://www.arg.dundee.ac.uk/aif#"
    assert payload["@type"] == "aif:ArgumentNetwork"
    assert payload["issue"] == "housing"
    assert len(payload["@graph"]) == 3
    assert len(payload["nodes"]) == 2
    assert payload["nodes"][0]["@id"] == "arg-1-premise"
    assert payload["edges"][0]["relation"] == "support"
    json.dumps(payload)


def test_policy_graph_namespaces_duplicate_component_ids() -> None:
    """Graph export should not merge same component IDs from different records."""
    records = [
        PipelineRecord(
            doc_id="speech-1",
            corpus_source="hansard",
            raw_text="Because rents are rising, the bill should pass.",
            cleaned_tokens=[],
            nz_act_citations=[],
            te_reo_terms=[],
            arguments=[
                {
                    "component_id": "arg-1-premise",
                    "component_type": "premise",
                    "text": "Because rents are rising",
                    "start": 0,
                    "end": 24,
                    "confidence": 0.9,
                },
                {
                    "component_id": "arg-1-conclusion",
                    "component_type": "conclusion",
                    "text": "the bill should pass",
                    "start": 26,
                    "end": 46,
                    "confidence": 0.9,
                },
            ],
        ),
        PipelineRecord(
            doc_id="speech-2",
            corpus_source="hansard",
            raw_text="Because emissions are rising, the bill should pass.",
            cleaned_tokens=[],
            nz_act_citations=[],
            te_reo_terms=[],
            arguments=[
                {
                    "component_id": "arg-1-premise",
                    "component_type": "premise",
                    "text": "Because emissions are rising",
                    "start": 0,
                    "end": 28,
                    "confidence": 0.9,
                },
                {
                    "component_id": "arg-1-conclusion",
                    "component_type": "conclusion",
                    "text": "the bill should pass",
                    "start": 30,
                    "end": 50,
                    "confidence": 0.9,
                },
            ],
        ),
    ]

    payload = export_argument_graph_jsonld(records, issue="climate")
    node_ids = {node["@id"] for node in payload["nodes"]}

    assert len(payload["nodes"]) == 4
    assert "arg-1-premise" in node_ids
    assert "speech-2:arg-1-premise" in node_ids
