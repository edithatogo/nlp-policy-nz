"""Voting record parser for New Zealand Hansard division records."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class MemberVote:
    """An individual MP's vote in a division."""

    member_name: str
    vote: str  # 'aye' | 'nay' | 'abstain'
    party: str | None = None

@dataclass
class DivisionRecord:
    """Parsed parliamentary voting (division) record."""

    motion: str
    ayes_count: int = 0
    nays_count: int = 0
    abstains_count: int = 0
    outcome: str = "defeated"  # 'passed' | 'defeated'
    votes: list[MemberVote] = field(default_factory=list)
    party_votes: dict[str, dict[str, int]] = field(default_factory=dict) # party_name -> {'aye': count, 'nay': count}

def parse_division(text: str) -> DivisionRecord | None:
    """Parse a Hansard division text segment and extract voting details.

    Supports both party voting patterns and conscience/personal voting lists.
    """
    if not text or not text.strip():
        return None

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # 1. Extract motion
    # Look for "The question is..." or general motion headers
    motion = "Unknown Motion"
    for line in lines:
        if "question is" in line.lower() or "motion" in line.lower() or "read a third time" in line.lower():
            motion = line
            break
    if motion == "Unknown Motion" and lines:
        motion = lines[0]

    ayes_count = 0
    nays_count = 0
    abstains_count = 0
    votes = []
    party_votes = {}

    # Regular expressions for party voting
    # e.g., "National: 49 votes ayes" or "Labour: 34 ayes" or "Green Party (15 ayes)"
    party_aye_pattern = re.compile(r"(\b[A-Za-z\s]+?)\b(?:\s*\(?\s*(\d+)\s*(?:votes?\s*)?ayes?\)?|\s*:\s*(\d+)\s*(?:votes?\s*)?ayes?)", re.IGNORECASE)
    party_nay_pattern = re.compile(r"(\b[A-Za-z\s]+?)\b(?:\s*\(?\s*(\d+)\s*(?:votes?\s*)?nays?|\s*:\s*(\d+)\s*(?:votes?\s*)?nays?|\s*\(?\s*(\d+)\s*(?:votes?\s*)?noes?\)?|\s*:\s*(\d+)\s*(?:votes?\s*)?noes?)", re.IGNORECASE)

    # Regular expressions for conscience voting lists
    # e.g., "Ayes: Luxon, Willis, Bishop"
    ayes_list_match = re.search(r"(?:Ayes\s*:\s*|Ayes\s*—\s*)(.*)", text, re.IGNORECASE)
    noes_list_match = re.search(r"(?:Noes\s*:\s*|Noes\s*—\s*|Nays\s*:\s*)(.*)", text, re.IGNORECASE)

    if ayes_list_match or noes_list_match:
        # 2. Process conscience votes
        if ayes_list_match:
            names = [n.strip() for n in ayes_list_match.group(1).split(";") if n.strip()]
            if len(names) <= 1:
                names = [n.strip() for n in ayes_list_match.group(1).split(",") if n.strip()]
            for name in names:
                # Stop if we hit Noes list marker
                if "noes" in name.lower() or "nays" in name.lower():
                    break
                party = resolve_member_party(name)
                votes.append(MemberVote(member_name=name, vote="aye", party=party))
                ayes_count += 1

        if noes_list_match:
            names = [n.strip() for n in noes_list_match.group(1).split(";") if n.strip()]
            if len(names) <= 1:
                names = [n.strip() for n in noes_list_match.group(1).split(",") if n.strip()]
            for name in names:
                party = resolve_member_party(name)
                votes.append(MemberVote(member_name=name, vote="nay", party=party))
                nays_count += 1
    else:
        # 3. Process party votes line by line
        for line in lines:
            # Check for total counts line, e.g., "Ayes 68, Noes 52"
            re.search(r"(?:Ayes\s*(\d+)|Noes\s*(\d+)|Nays\s*(\d+))", line, re.IGNORECASE)

            aye_matches = party_aye_pattern.findall(line)
            for match in aye_matches:
                party = match[0].strip()
                # Skip words like "total" or "party" if isolated
                if party.lower() in ("total", "ayes", "noes", "nays"):
                    continue
                cnt = int(match[1] or match[2])
                if party not in party_votes:
                    party_votes[party] = {"aye": 0, "nay": 0}
                party_votes[party]["aye"] += cnt
                ayes_count += cnt

            nay_matches = party_nay_pattern.findall(line)
            for match in nay_matches:
                party = match[0].strip()
                if party.lower() in ("total", "ayes", "noes", "nays"):
                    continue
                cnt = int(match[1] or match[2] or match[3] or match[4])
                if party not in party_votes:
                    party_votes[party] = {"aye": 0, "nay": 0}
                party_votes[party]["nay"] += cnt
                nays_count += cnt

    # Overall outcome computation
    outcome = "passed" if ayes_count > nays_count else "defeated"

    return DivisionRecord(
        motion=motion,
        ayes_count=ayes_count,
        nays_count=nays_count,
        abstains_count=abstains_count,
        outcome=outcome,
        votes=votes,
        party_votes=party_votes
    )

MP_PARTY_KB: dict[str, str] = {
    "luxon": "National",
    "willis": "National",
    "bishop": "National",
    "hipkins": "Labour",
    "sepuloni": "Labour",
    "swarbrick": "Green",
    "seymour": "ACT",
    "peters": "NZ First",
}

def resolve_member_party(member_name: str) -> str | None:
    """Resolve a member's party affiliation from their name using the KB."""
    # Clean name (e.g. "Luxon, Christopher" -> "luxon")
    clean = re.sub(r"[^a-zA-Z\s]", "", member_name).lower()
    for key, party in MP_PARTY_KB.items():
        if key in clean:
            return party
    return None
