"""Tests for temporal expression extraction and TimeML-style annotations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import spacy

from nlp_policy_nz.legal.temporal import (
    TemporalExpression,
    TemporalGraph,
    TemporalType,
    detect_temporal_expressions,
)
from nlp_policy_nz.storage.serialization import (
    PipelineRecord,
    load_from_parquet,
    serialize_to_parquet,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_detects_and_normalizes_core_timex_types() -> None:
    """Extractor should classify DATE, TIME, DURATION, and SET expressions."""
    text = (
        "Section 2 comes into force on 1 July 2024. "
        "The Minister must decide within 28 days, at 5 pm. "
        "Reports are required every 6 months."
    )

    annotations = detect_temporal_expressions(text, spacy.blank("en"))

    by_type = {annotation.timex_type: annotation for annotation in annotations}
    assert by_type[TemporalType.DATE].normalized == "2024-07-01"
    assert by_type[TemporalType.DATE].role == "commencement"
    assert by_type[TemporalType.TIME].normalized == "17:00"
    assert by_type[TemporalType.DURATION].normalized == "P28D"
    assert by_type[TemporalType.DURATION].role == "deadline"
    assert by_type[TemporalType.SET].normalized == "P6M"
    assert by_type[TemporalType.SET].role == "recurrence"


def test_spacy_component_sets_doc_extension() -> None:
    """The spaCy component stores temporal annotations on the Doc."""
    nlp = spacy.blank("en")
    nlp.add_pipe("temporal_extractor")

    doc = nlp("This Act commences on 15 March 2025.")

    assert doc._.temporal_expressions
    annotation = doc._.temporal_expressions[0]
    assert annotation.text == "15 March 2025"
    assert annotation.normalized == "2025-03-15"


def test_named_recurrence_iso_date_midnight_and_section_inference() -> None:
    """Additional forms should normalize and infer nearby section identifiers."""
    text = "Section 7 is effective from 2024-09-01 and reports are due annually at 12 am."

    annotations = detect_temporal_expressions(text, spacy.blank("en"))

    assert annotations[0].normalized == "2024-09-01"
    assert annotations[0].role == "effective"
    assert annotations[0].section_id == "s7"
    by_type = {annotation.timex_type: annotation for annotation in annotations}
    assert by_type[TemporalType.TIME].normalized == "00:00"
    assert by_type[TemporalType.SET].normalized == "P1Y"


def test_invalid_calendar_dates_are_not_normalized() -> None:
    """Invalid calendar dates should not be emitted as ISO 8601 annotations."""
    text = (
        "This Act commences on 31 February 2024. "
        "The review date is 2024-99-99. "
        "The valid fallback date is 29 February 2024."
    )

    annotations = detect_temporal_expressions(text, spacy.blank("en"))

    assert [annotation.normalized for annotation in annotations] == ["2024-02-29"]


def test_temporal_expression_serializes_to_pipeline_dict() -> None:
    """Temporal expressions should serialize as plain schema-safe dictionaries."""
    annotation = TemporalExpression(
        timex_type=TemporalType.DATE,
        text="1 July 2024",
        normalized="2024-07-01",
        start=30,
        end=41,
        signal="on",
        role="commencement",
        section_id="s2",
    )

    assert annotation.to_dict() == {
        "timex_type": "DATE",
        "text": "1 July 2024",
        "normalized": "2024-07-01",
        "start": 30,
        "end": 41,
        "signal": "on",
        "role": "commencement",
        "section_id": "s2",
    }


def test_temporal_graph_links_effective_periods() -> None:
    """Temporal graph queries should return active sections for ISO dates."""
    graph = TemporalGraph()
    graph.add_section("s2", title="Commencement")
    graph.link_temporal_expression(
        "s2",
        TemporalExpression(
            timex_type=TemporalType.DATE,
            text="1 July 2024",
            normalized="2024-07-01",
            start=0,
            end=11,
            role="commencement",
        ),
    )
    graph.add_effective_period("s3", start="2024-08-01", end="2025-01-31")

    assert graph.effective_period("s2") == ("2024-07-01", None)
    assert graph.graph.has_edge("s2", "time:s2:2024-07-01")
    assert graph.graph.nodes["time:s2:2024-07-01"]["timex_type"] == "DATE"
    assert graph.find_active_sections("2024-06-30") == []
    assert graph.find_active_sections("2024-08-15") == ["s2", "s3"]
    assert graph.find_active_sections("2025-02-01") == ["s2"]


def test_temporal_graph_handles_deadlines_non_dates_and_missing_sections() -> None:
    """Graph should ignore non-date bounds and expose missing periods as empty."""
    graph = TemporalGraph()
    graph.link_temporal_expression(
        "s4",
        TemporalExpression(
            timex_type=TemporalType.DATE,
            text="31 December 2024",
            normalized="2024-12-31",
            start=0,
            end=16,
            role="expiry",
        ),
    )
    graph.link_temporal_expression(
        "s4",
        TemporalExpression(
            timex_type=TemporalType.DURATION,
            text="within 20 days",
            normalized="P20D",
            start=20,
            end=34,
            role="deadline",
        ),
    )

    assert graph.effective_period("s4") == (None, "2024-12-31")
    assert graph.effective_period("missing") == (None, None)
    assert graph.find_active_sections("2025-01-01") == []


def test_pipeline_record_preserves_temporal_expressions(tmp_path: Path) -> None:
    """PipelineRecord and Parquet serialization should retain temporal annotations."""
    record = PipelineRecord(
        doc_id="leg-commencement",
        corpus_source="legislation",
        raw_text="This Act commences on 1 July 2024.",
        cleaned_tokens=["This", "Act", "commences"],
        nz_act_citations=[],
        te_reo_terms=[],
        temporal_expressions=[
            {
                "timex_type": "DATE",
                "text": "1 July 2024",
                "normalized": "2024-07-01",
                "start": 22,
                "end": 33,
                "signal": "on",
                "role": "commencement",
                "section_id": None,
            }
        ],
    )

    parquet_path = tmp_path / "temporal.parquet"
    serialize_to_parquet([record], parquet_path)
    loaded = load_from_parquet(parquet_path)

    assert loaded[0].temporal_expressions == record.temporal_expressions
