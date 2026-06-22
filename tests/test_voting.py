"""Tests for Hansard voting record parsing."""

from __future__ import annotations

from nlp_policy_nz.parliament.voting import parse_division, resolve_member_party


def test_parse_empty_division_returns_none() -> None:
    """Empty division text is ignored."""
    assert parse_division("") is None


def test_parse_conscience_division() -> None:
    """Parser extracts MP-level conscience division votes."""
    division_text = (
        "Speaker: The question is that the amendment be agreed to.\n"
        "Ayes: Luxon, Christopher; Willis, Nicola; Bishop, Chris\n"
        "Noes: Hipkins, Chris; Sepuloni, Carmel"
    )

    record = parse_division(division_text)

    assert record is not None
    assert "amendment be agreed to" in record.motion
    assert record.ayes_count == 3
    assert record.nays_count == 2
    assert record.outcome == "passed"
    assert len(record.votes) == 5
    assert record.votes[0].member_name == "Luxon, Christopher"
    assert record.votes[0].vote == "aye"
    assert record.votes[0].party == "National"
    assert record.votes[3].member_name == "Hipkins, Chris"
    assert record.votes[3].vote == "nay"
    assert record.votes[3].party == "Labour"


def test_parse_party_division() -> None:
    """Parser extracts party-level division tallies."""
    division_text = (
        "The question is that the bill be now read a third time.\n"
        "National 49 votes ayes\n"
        "Labour 34 votes noes\n"
        "Green Party 15 votes ayes\n"
        "ACT New Zealand 11 votes ayes\n"
    )

    record = parse_division(division_text)

    assert record is not None
    assert "read a third time" in record.motion
    assert record.ayes_count == 75
    assert record.nays_count == 34
    assert record.outcome == "passed"
    assert "National" in record.party_votes
    assert record.party_votes["National"]["aye"] == 49
    assert record.party_votes["Labour"]["nay"] == 34


def test_parse_party_division_updates_existing_party_tallies() -> None:
    """Parser aggregates aye and nay entries for the same party."""
    division_text = (
        "Vote on procedural motion.\n"
        "ACT New Zealand 1 votes ayes\n"
        "ACT New Zealand 2 votes noes\n"
    )

    record = parse_division(division_text)

    assert record is not None
    assert record.motion == "Vote on procedural motion."
    assert record.party_votes["ACT New Zealand"]["aye"] == 1
    assert record.party_votes["ACT New Zealand"]["nay"] == 2
    assert record.outcome == "defeated"


def test_parse_conscience_division_stops_at_inline_noes_marker() -> None:
    """Inline Noes marker ends the Ayes list before nay parsing."""
    division_text = "Ayes: Luxon, Christopher, Noes: Hipkins, Chris"

    record = parse_division(division_text)

    assert record is not None
    assert record.motion == division_text
    assert record.ayes_count == 2
    assert record.nays_count == 2
    assert record.outcome == "defeated"


def test_resolve_member_party_unknown_member() -> None:
    """Unknown MP names return no party affiliation."""
    assert resolve_member_party("Unknown Member") is None
