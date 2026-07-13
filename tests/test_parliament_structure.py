from __future__ import annotations

import pytest
from pydantic import ValidationError

from nlp_policy_nz.parliament.evaluation import EvaluationThresholds, evaluate_structure
from nlp_policy_nz.parliament.structure import (
    CallableStructureAdapter,
    OCRAlternative,
    ParliamentaryNode,
    SourceSpan,
    StructureDocument,
    export_structure_jsonld,
    reconstruct_structure,
)


def test_source_spans_are_forward_and_page_grounded() -> None:
    span = SourceSpan(page_id="page-1", block_id="block-1", start=2, end=7, text="Hello")

    assert span.end - span.start == len(span.text)
    with pytest.raises(ValidationError):
        SourceSpan(page_id="page-1", block_id="block-1", start=7, end=2, text="Hello")


def test_parliamentary_node_rejects_unknown_types() -> None:
    with pytest.raises(ValidationError):
        ParliamentaryNode(
            node_id="page-1",
            node_type="unknown",
            label="Unknown",
            sequence=0,
            source_spans=(),
        )


def test_reconstruct_structure_builds_hierarchy_speaker_and_citation_links() -> None:
    text = (
        "SESSION 12\n"
        "SITTING 4\n"
        "12 March 1961\n"
        "QUESTIONS\n"
        "Hon Alice Smith: The Crimes Act 1961 applies to this petition.\n"
        "Mr Bob Jones: I support the question.\n"
        "DIVISION\n"
    )

    result = reconstruct_structure(page_id="page-1", text=text)

    assert [node.node_type for node in result.nodes] == [
        "page",
        "session",
        "sitting",
        "date",
        "question",
        "speech",
        "speech",
        "division",
    ]
    speech_nodes = [node for node in result.nodes if node.node_type == "speech"]
    assert speech_nodes[0].parent_id == result.nodes[4].node_id
    assert result.speakers[0].surface_form == "Hon Alice Smith"
    assert result.speakers[0].canonical_name == "Alice Smith"
    assert any(link.relation == "cites_legislation" for link in result.links)
    assert result.review_queue == ()


def test_ambiguous_speaker_is_abstained_and_queued_for_review() -> None:
    result = reconstruct_structure(
        page_id="page-2",
        text="DEBATE\nMember: The question is before the House.\n",
    )

    assert result.speakers[0].abstained is True
    assert result.speakers[0].identity_id is None
    assert result.review_queue[0].kind == "speaker_attribution"
    assert result.review_queue[0].reason


def test_reconstruction_preserves_line_offsets() -> None:
    text = "APPENDIX A\nMr Speaker: Hello.\n"

    result = reconstruct_structure(page_id="page-3", text=text)
    speech = next(node for node in result.nodes if node.node_type == "speech")
    span = speech.source_spans[0]

    assert text[span.start : span.end] == span.text


def test_speeches_share_their_container_and_link_spans_handle_indentation() -> None:
    text = (
        "DEBATE\n"
        "  Hon Alice Smith: The Crimes Act 1961 applies.\n"
        "  Mr Bob Jones: Wellington is mentioned.\n"
    )

    result = reconstruct_structure("page-3b", text)
    speeches = [node for node in result.nodes if node.node_type == "speech"]
    debate = next(node for node in result.nodes if node.node_type == "debate")
    place_link = next(link for link in result.links if link.relation == "mentions_place")

    assert [speech.parent_id for speech in speeches] == [debate.node_id, debate.node_id]
    place_span = place_link.source_spans[0]
    assert text[place_span.start : place_span.end] == "Wellington"


def test_volume_and_interjection_are_explicit_node_types() -> None:
    result = reconstruct_structure("page-3c", "VOLUME 3\nINTERJECTION\n")

    assert [node.node_type for node in result.nodes] == ["page", "volume", "interjection"]


def test_source_span_can_carry_token_and_ocr_alternative_provenance() -> None:
    alternative = OCRAlternative(engine="surya", text="Helo", confidence=0.4)
    span = SourceSpan(
        page_id="page-3d",
        block_id="block-1",
        start=0,
        end=5,
        text="Hello",
        token_ids=("token-1",),
        ocr_alternatives=(alternative,),
    )

    assert span.token_ids == ("token-1",)
    assert span.ocr_alternatives[0].engine == "surya"


def test_adapter_and_jsonld_export_preserve_page_identity() -> None:
    adapter = CallableStructureAdapter(reconstruct_structure)
    document = adapter.reconstruct("page-4", "DEBATE\nMr Speaker: The Crimes Act 1961 applies.\n")
    payload = export_structure_jsonld(document)

    assert payload["@context"]["sourceSpan"] == "https://schema.org/hasPart"
    assert payload["@graph"][0]["@id"].startswith("urn:hathi:page-4:")
    assert payload["@graph"][0]["pageId"] == "page-4"

    mismatched = CallableStructureAdapter(
        lambda _page, _text: reconstruct_structure("other-page", "")
    )
    with pytest.raises(ValueError, match="different page_id"):
        mismatched.reconstruct("page-4", "")


def test_jsonld_export_includes_speakers_and_review_items() -> None:
    document = reconstruct_structure("page-4b", "Member: The question is before the House.\n")

    payload = export_structure_jsonld(document)
    graph_types = {item["@type"] for item in payload["@graph"]}

    assert "hathi:speakerAttribution" in graph_types
    assert "hathi:reviewItem" in graph_types


def test_evaluation_reports_structure_speaker_link_and_span_scores() -> None:
    text = "DEBATE\nHon Alice Smith: The Crimes Act 1961 applies.\n"
    reference = reconstruct_structure(page_id="page-5", text=text)
    candidate = reconstruct_structure(page_id="page-5", text=text)

    result = evaluate_structure(reference, candidate)

    assert result.structure_accuracy == 1
    assert result.speaker_accuracy == 1
    assert result.link_f1 == 1
    assert result.span_fidelity == 1
    assert result.abstention_recall == 1
    assert result.passed is True


def test_evaluation_fails_closed_for_mismatched_pages_and_missing_links() -> None:
    reference = reconstruct_structure("page-6", "Hon Alice Smith: The Crimes Act 1961 applies.\n")
    candidate = StructureDocument(
        page_id="page-6",
        nodes=reference.nodes,
        speakers=reference.speakers,
        links=(),
        review_queue=reference.review_queue,
    )

    result = evaluate_structure(
        reference,
        candidate,
        thresholds=EvaluationThresholds(min_link_f1=1),
    )

    assert result.passed is False
    assert set(result.failures) == {"link_f1", "span_fidelity"}
    with pytest.raises(ValueError, match="same page"):
        evaluate_structure(reference, reference.model_copy(update={"page_id": "other"}))
