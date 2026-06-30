"""Amendment detection, bill version diffing, and lifecycle graph tracking."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

import defusedxml.ElementTree
import networkx as nx

AMENDMENT_TYPES = {"substantive", "technical", "sop"}
TECHNICAL_MARKERS = {
    "comma",
    "correct",
    "cross-reference",
    "drafting",
    "grammar",
    "minor",
    "spelling",
    "technical",
    "typographical",
    "typo",
}


@dataclass(frozen=True)
class Amendment:
    """A legislative amendment extracted from Hansard or committee reports."""

    proposer: str
    target_clause: str
    text: str
    amendment_type: str
    sop_number: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible representation."""
        return asdict(self)


def parse_amendment(text: str) -> Amendment | None:
    """Parse one debate or committee text block into an amendment."""
    amendments = parse_amendments(text)
    return amendments[0] if amendments else None


def parse_amendments(text: str) -> list[Amendment]:
    """Parse one or more amendment references from Hansard-style text."""
    if not text or not text.strip():
        return []

    amendments: list[Amendment] = []
    for segment in _amendment_segments(text):
        proposer = _extract_proposer(segment)
        target_clause = _extract_target_clause(segment)
        sop_number = _extract_sop_number(segment)
        amendment_type = _classify_amendment(segment, sop_number=sop_number)
        amendments.append(
            Amendment(
                proposer=proposer,
                target_clause=target_clause,
                text=segment.strip(),
                amendment_type=amendment_type,
                sop_number=sop_number,
            )
        )
    return amendments


def diff_bill_versions(v1: str, v2: str) -> dict[str, list[str]]:
    """Structurally compare two XML or JSON bill versions."""
    before = _extract_xml_nodes(v1)
    after = _extract_xml_nodes(v2)
    if not before and not after:
        before = _extract_json_nodes(v1)
        after = _extract_json_nodes(v2)
    return _compare_node_maps(before, after)


class AmendmentLifecycleGraph:
    """NetworkX directed graph modeling an amendment's progression."""

    STATES = ("proposed", "debated", "voted", "passed", "defeated")

    def __init__(self, amendment_id: str) -> None:
        """Create a lifecycle graph for one amendment identifier."""
        self.amendment_id = amendment_id
        self.graph = nx.DiGraph(amendment_id=amendment_id)
        self.graph.add_nodes_from(
            [
                ("proposed", {"description": "Amendment proposed or tabled"}),
                ("debated", {"description": "Amendment debated in the House"}),
                ("voted", {"description": "Vote called on amendment"}),
                ("passed", {"description": "Amendment agreed to and passed"}),
                ("defeated", {"description": "Amendment rejected and defeated"}),
            ]
        )

    @classmethod
    def from_amendment(
        cls,
        amendment: Amendment,
        *,
        amendment_id: str,
    ) -> AmendmentLifecycleGraph:
        """Create a graph seeded with amendment metadata."""
        lifecycle = cls(amendment_id)
        lifecycle.graph.nodes["proposed"].update(amendment.to_dict())
        return lifecycle

    def add_event(
        self,
        from_state: str,
        to_state: str,
        date: str,
        **metadata: str,
    ) -> None:
        """Add a transition event in the lifecycle."""
        if from_state not in self.STATES or to_state not in self.STATES:
            msg = f"Unknown amendment lifecycle transition: {from_state} -> {to_state}"
            raise ValueError(msg)
        self.graph.add_edge(from_state, to_state, date=date, **metadata)

    def get_current_status(self) -> str:
        """Return the furthest status reachable from the proposed state."""
        for state in ("passed", "defeated", "voted", "debated"):
            if nx.has_path(self.graph, "proposed", state):
                return state
        return "proposed" if self.graph.has_node("proposed") else "unknown"

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible graph summary."""
        return {
            "amendment_id": self.amendment_id,
            "status": self.get_current_status(),
            "events": [
                {"from": source, "to": target, **data}
                for source, target, data in self.graph.edges(data=True)
            ],
        }


def amendments_to_dicts(amendments: Sequence[Amendment]) -> list[dict[str, str | None]]:
    """Convert amendments to JSON-compatible dictionaries."""
    return [amendment.to_dict() for amendment in amendments]


def _amendment_segments(text: str) -> list[str]:
    """Split text into candidate amendment-bearing segments."""
    normalised = re.sub(r"\s+", " ", text.strip())
    raw_segments = re.split(r"(?<=[.;])\s+|\n+", normalised)
    return [segment.strip() for segment in raw_segments if _is_amendment_segment(segment)]


def _is_amendment_segment(segment: str) -> bool:
    """Return whether a segment describes a proposed amendment."""
    if re.search(r"\b(?:SOP|Supplementary Order Paper)\b", segment, re.IGNORECASE):
        return True
    return bool(
        re.search(
            r"\b(?:moved|proposed|introduced|tabled|rose)\b.*\bamend(?:ment|ed|s)?\b",
            segment,
            re.IGNORECASE,
        )
    )


def _extract_proposer(segment: str) -> str:
    """Extract an MP proposer name from an amendment segment."""
    pattern = re.compile(
        r"(?:Hon\s+)?(?P<name>[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){0,3})"
        r"\s+(?:moved|proposed|introduced|tabled|rose)",
    )
    match = pattern.search(segment)
    if match:
        return match.group("name").strip()
    colon_match = re.match(
        r"(?:Hon\s+)?(?P<name>[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){0,3})\s*:",
        segment,
    )
    return colon_match.group("name").strip() if colon_match else "Unknown Proposer"


def _extract_target_clause(segment: str) -> str:
    """Extract the legal clause or section targeted by an amendment."""
    match = re.search(
        r"\b(?P<label>clause|section|schedule|paragraph|para)\s+"
        r"(?P<number>\d+(?:\(\d+\))?[A-Za-z]?)",
        segment,
        re.IGNORECASE,
    )
    if not match:
        return "Unknown Clause"
    return f"{match.group('label').lower()} {match.group('number')}"


def _extract_sop_number(segment: str) -> str | None:
    """Extract a Supplementary Order Paper number."""
    match = re.search(
        r"\b(?:SOP|Supplementary\s+Order\s+Paper)\s*(?:No\.?\s*)?(?P<number>\d+)",
        segment,
        re.IGNORECASE,
    )
    return match.group("number") if match else None


def _classify_amendment(segment: str, *, sop_number: str | None) -> str:
    """Classify an amendment as SOP, technical, or substantive."""
    if sop_number is not None:
        return "sop"
    lowered = segment.lower()
    if any(marker in lowered for marker in TECHNICAL_MARKERS):
        return "technical"
    return "substantive"


def _extract_xml_nodes(text: str) -> dict[str, str]:
    """Extract legal structural nodes from XML text."""
    try:
        root = defusedxml.ElementTree.fromstring(text)
    except defusedxml.ElementTree.ParseError:
        return {}
    nodes: dict[str, str] = {}
    for element in root.iter():
        tag = _strip_namespace(element.tag).lower()
        identifier = element.attrib.get("id") or element.attrib.get("eId")
        if identifier and tag in {"clause", "section", "schedule", "paragraph"}:
            nodes[identifier] = _normalise_node_text(" ".join(element.itertext()))
    return nodes


def _extract_json_nodes(text: str) -> dict[str, str]:
    """Extract structural bill nodes from JSON text."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    nodes: dict[str, str] = {}
    _walk_json(payload, nodes)
    return nodes


def _walk_json(value: object, nodes: dict[str, str]) -> None:
    """Populate *nodes* from nested JSON bill structures."""
    if isinstance(value, Mapping):
        identifier = _json_identifier(value)
        if identifier is not None:
            nodes[identifier] = _normalise_json_node(value)
        for child in value.values():
            _walk_json(child, nodes)
    elif isinstance(value, list):
        for item in value:
            _walk_json(item, nodes)


def _json_identifier(value: Mapping[str, object]) -> str | None:
    """Return a legal node identifier from a mapping."""
    for key in ("id", "eId", "number", "clause_id", "section_id"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def _normalise_json_node(value: Mapping[str, object]) -> str:
    """Return a stable comparable representation for a JSON node."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _compare_node_maps(before: dict[str, str], after: dict[str, str]) -> dict[str, list[str]]:
    """Compare two identifier-to-content maps."""
    return {
        "added": sorted(node_id for node_id in after if node_id not in before),
        "modified": sorted(
            node_id for node_id in after if node_id in before and after[node_id] != before[node_id]
        ),
        "repealed": sorted(node_id for node_id in before if node_id not in after),
    }


def _strip_namespace(tag: str) -> str:
    """Remove an XML namespace from a tag name."""
    return tag.rsplit("}", 1)[-1]


def _normalise_node_text(text: str) -> str:
    """Normalize structural node text for comparison."""
    return re.sub(r"\s+", " ", text).strip()
