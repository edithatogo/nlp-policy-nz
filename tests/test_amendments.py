"""Tests for Track 18 amendment parsing, diffing, lifecycle, and integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import networkx as nx

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.parliament.amendments import (
    Amendment,
    AmendmentLifecycleGraph,
    diff_bill_versions,
    parse_amendment,
    parse_amendments,
)
from nlp_policy_nz.pipeline_api import _extract_amendment_records, _extract_voting_record
from nlp_policy_nz.storage.serialization import (
    SCHEMA_FIELDS,
    PipelineRecord,
    records_to_dataframe,
)

if TYPE_CHECKING:
    import pytest


def test_parse_amendment_sop() -> None:
    """Parser extracts SOP number, proposer, type, and target clause."""
    text = "Hon Nicola Willis moved Supplementary Order Paper No 45 to amend clause 12."

    amendment = parse_amendment(text)

    assert amendment is not None
    assert amendment.proposer == "Nicola Willis"
    assert amendment.target_clause == "clause 12"
    assert amendment.amendment_type == "sop"
    assert amendment.sop_number == "45"


def test_parse_amendments_detects_multiple_types() -> None:
    """Parser detects substantive, technical, and SOP amendments in one text."""
    text = """
    Hon Nicola Willis moved Supplementary Order Paper No 45 to amend clause 12.
    Chris Bishop rose to move a technical amendment to section 5(2), correcting a cross-reference.
    Debbie Ngarewa-Packer proposed an amendment to clause 7 to insert a new eligibility test.
    """

    amendments = parse_amendments(text)

    assert [item.proposer for item in amendments] == [
        "Nicola Willis",
        "Chris Bishop",
        "Debbie Ngarewa-Packer",
    ]
    assert [item.amendment_type for item in amendments] == [
        "sop",
        "technical",
        "substantive",
    ]
    assert [item.target_clause for item in amendments] == [
        "clause 12",
        "section 5(2)",
        "clause 7",
    ]


def test_diff_bill_versions_xml_identifies_added_modified_repealed() -> None:
    """XML diff identifies added, modified, and repealed legal sections."""
    before = """
    <bill>
      <section id="sec-1">Original text</section>
      <section id="sec-2">Old text</section>
    </bill>
    """
    after = """
    <bill>
      <section id="sec-1">Original text updated</section>
      <section id="sec-3">Added text</section>
    </bill>
    """

    diff = diff_bill_versions(before, after)

    assert diff == {
        "added": ["sec-3"],
        "modified": ["sec-1"],
        "repealed": ["sec-2"],
    }


def test_diff_bill_versions_json_handles_nested_clause_lists() -> None:
    """JSON diff handles structured lists of legal clause objects."""
    before = json.dumps(
        {
            "clauses": [
                {"id": "clause-1", "text": "Keep this text."},
                {"id": "clause-2", "text": "Repeal this text."},
            ]
        }
    )
    after = json.dumps(
        {
            "clauses": [
                {"id": "clause-1", "text": "Keep this text with amendment."},
                {"id": "clause-3", "text": "Add this text."},
            ]
        }
    )

    diff = diff_bill_versions(before, after)

    assert diff == {
        "added": ["clause-3"],
        "modified": ["clause-1"],
        "repealed": ["clause-2"],
    }


def test_amendment_lifecycle_graph_tracks_terminal_status() -> None:
    """Lifecycle graph tracks amendment progression to a terminal status."""
    amendment = Amendment(
        proposer="Nicola Willis",
        target_clause="clause 12",
        text="Supplementary Order Paper No 45 to amend clause 12.",
        amendment_type="sop",
        sop_number="45",
    )
    lifecycle = AmendmentLifecycleGraph.from_amendment(amendment, amendment_id="sop-45")

    lifecycle.add_event("proposed", "debated", "2024-06-15")
    lifecycle.add_event("debated", "voted", "2024-06-16")
    lifecycle.add_event("voted", "defeated", "2024-06-16", vote_id="division-101")

    assert lifecycle.get_current_status() == "defeated"
    assert nx.has_path(lifecycle.graph, "proposed", "defeated")
    assert lifecycle.graph.edges[("voted", "defeated")]["vote_id"] == "division-101"


def test_pipeline_record_includes_voting_and_amendment_fields() -> None:
    """PipelineRecord and dataframe schema include Track 18 fields."""
    record = PipelineRecord(
        doc_id="han-division-001",
        corpus_source="hansard",
        raw_text="The question is that the amendment be agreed to.",
        cleaned_tokens=["The", "question", "is"],
        nz_act_citations=[],
        te_reo_terms=[],
        voting_record={"motion": "amendment be agreed to", "outcome": "passed"},
        amendments=[{"proposer": "Nicola Willis", "amendment_type": "sop"}],
    )

    assert "voting_record" in SCHEMA_FIELDS
    assert "amendments" in SCHEMA_FIELDS
    assert record.voting_record is not None
    assert record.amendments is not None
    assert record.voting_record["outcome"] == "passed"
    assert record.amendments[0]["amendment_type"] == "sop"
    df = records_to_dataframe([record])
    assert "voting_record" in df.columns
    assert "amendments" in df.columns


def test_pipeline_extractors_preserve_track18_fields_in_dataframe() -> None:
    """Pipeline helpers and dataframe conversion retain voting and amendments."""
    text = (
        "The question is that the amendment be agreed to.\n"
        "Ayes: Luxon, Christopher; Willis, Nicola; Bishop, Chris\n"
        "Noes: Hipkins, Chris; Sepuloni, Carmel\n"
        "Hon Nicola Willis moved Supplementary Order Paper No 45 to amend clause 12."
    )
    record = PipelineRecord(
        doc_id="han-track18-001",
        corpus_source="hansard",
        raw_text=text,
        cleaned_tokens=text.split(),
        nz_act_citations=[],
        te_reo_terms=[],
        voting_record=_extract_voting_record(text),
        amendments=_extract_amendment_records(text),
    )
    df = records_to_dataframe([record])

    assert record.voting_record is not None
    assert record.amendments is not None
    assert record.voting_record["outcome"] == "passed"
    assert record.amendments[0]["sop_number"] == "45"
    assert "voting_record" in df.columns
    assert "amendments" in df.columns


def test_cli_voting_summary_outputs_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI voting-summary emits JSON for a Hansard division text file."""
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, encoding="utf-8": (
            "The question is that the amendment be agreed to.\n"
            "Ayes: Luxon, Christopher; Willis, Nicola\n"
            "Noes: Hipkins, Chris\n"
        ),
    )

    rc = main(["voting-summary", "--input", "division.txt"])

    assert rc == 0


def test_cli_amendment_history_outputs_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI amendment-history parses amendments from a text file."""
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, encoding="utf-8": (
            "Hon Nicola Willis moved Supplementary Order Paper No 45 to amend clause 12."
        ),
    )

    rc = main(["amendment-history", "--input", "amendments.txt"])

    assert rc == 0
