import pytest
from nlp_policy_nz.parliament.voting import parse_division, DivisionRecord

def test_parse_conscience_division():
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

def test_parse_party_division():
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
