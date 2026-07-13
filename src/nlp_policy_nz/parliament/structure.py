"""Page-grounded reconstruction of historical parliamentary structure."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

NodeType = Literal[
    "volume",
    "session",
    "sitting",
    "date",
    "page",
    "debate",
    "question",
    "speech",
    "interjection",
    "division",
    "table",
    "appendix",
]
LinkRelation = Literal[
    "cites_legislation",
    "mentions_agency",
    "mentions_place",
    "mentions_iwi",
    "references_committee",
    "references_petition",
    "cites_publication",
]

_DATE_PATTERN = re.compile(
    r"^(?:\d{1,2}\s+)?(?:January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+\d{4}$",
    re.IGNORECASE,
)
_SPEAKER_PATTERN = re.compile(r"^(?P<label>[A-Za-z][\w .,'\-\u2019]{1,100}):\s*(?P<body>.*)$")
_TITLE_PATTERN = re.compile(
    r"^(?P<title>Rt\s+Hon(?:ourable)?|Hon(?:ourable)?|Mr|Mrs|Ms|Dr|Madam|Speaker)\.?\s+",
    re.IGNORECASE,
)
_LEGISLATION_PATTERN = re.compile(
    r"\b(?:the\s+)?(?P<target>[A-Z][\w'.\-\u2019]*(?:\s+[A-Z][\w'.\-\u2019]*){0,5}\s+Act\s+\d{4})\b"
)
_AGENCY_PATTERN = re.compile(
    r"\b(?P<target>[A-Z][\w'.\-\u2019]*(?:\s+[A-Z][\w'.\-\u2019]*){0,4}\s+(?:Department|Ministry))\b"
)
_PLACE_PATTERN = re.compile(
    r"\b(?P<target>Auckland|Wellington|Otago|Canterbury|Waikato|North Island|South Island)\b"
)
_IWI_PATTERN = re.compile(
    r"\b(?P<target>[A-Z][\w'.\-\u2019]*(?:\s+[A-Z][\w'.\-\u2019]*){0,2}\s+(?:iwi|hap\u016b|hapu))\b",
    re.IGNORECASE,
)
_COMMITTEE_PATTERN = re.compile(
    r"\b(?P<target>[A-Z][\w'.\-\u2019]*(?:\s+[A-Z][\w'.\-\u2019]*){0,4}\s+Committee)\b"
)
_PETITION_PATTERN = re.compile(
    r"\bpetition(?:\s+of)?\s+(?P<target>[A-Z][\w'.\-\u2019]*(?:\s+[A-Z][\w'.\-\u2019]*){0,3})"
)
_PUBLICATION_PATTERN = re.compile(
    r"\b(?P<target>[A-Z][\w'.\-\u2019]*(?:\s+[A-Z][\w'.\-\u2019]*){0,5}\s+(?:Journal|Gazette|Report))\b"
)


class OCRAlternative(BaseModel):
    """An alternative OCR reading retained with engine provenance."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    engine: str = Field(min_length=1)
    text: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)


class SourceSpan(BaseModel):
    """A non-empty character span tied to one OCR/layout block."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_id: str = Field(min_length=1)
    block_id: str = Field(min_length=1)
    start: int = Field(ge=0)
    end: int = Field(ge=1)
    text: str = Field(min_length=1)
    token_ids: tuple[str, ...] = ()
    ocr_alternatives: tuple[OCRAlternative, ...] = ()

    @model_validator(mode="after")
    def validate_range(self) -> SourceSpan:
        """Ensure offsets are forward and match the captured text."""
        if self.end <= self.start or self.end - self.start != len(self.text):
            raise ValueError("source span must be a forward range matching its text")
        return self


class ParliamentaryNode(BaseModel):
    """A hierarchy node whose evidence remains page and block addressable."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str = Field(min_length=1)
    node_type: NodeType
    label: str = Field(min_length=1)
    sequence: int = Field(ge=0)
    parent_id: str | None = None
    source_spans: tuple[SourceSpan, ...]
    confidence: float = Field(default=1.0, ge=0, le=1)
    review_required: bool = False


class SpeakerAttribution(BaseModel):
    """Speaker surface form, normalized identity, and attribution uncertainty."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    speech_node_id: str = Field(min_length=1)
    surface_form: str = Field(min_length=1)
    identity_id: str | None = None
    canonical_name: str | None = None
    role: str | None = None
    valid_from: str | None = None
    valid_to: str | None = None
    confidence: float = Field(ge=0, le=1)
    abstained: bool = False
    source_spans: tuple[SourceSpan, ...]


class SemanticLink(BaseModel):
    """A candidate graph edge retaining the text that caused the link."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    subject_id: str = Field(min_length=1)
    relation: LinkRelation
    target_text: str = Field(min_length=1)
    target_id: str | None = None
    confidence: float = Field(ge=0, le=1)
    source_spans: tuple[SourceSpan, ...]
    review_required: bool = False


class ReviewItem(BaseModel):
    """Fail-closed queue item for a human or model-assisted review."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    source_spans: tuple[SourceSpan, ...]
    candidate_ids: tuple[str, ...] = ()


class StructureDocument(BaseModel):
    """Complete reconstruction output for one page or extracted document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_id: str = Field(min_length=1)
    nodes: tuple[ParliamentaryNode, ...]
    speakers: tuple[SpeakerAttribution, ...]
    links: tuple[SemanticLink, ...]
    review_queue: tuple[ReviewItem, ...]


class StructureAdapter(Protocol):
    """Contract for deterministic or model-backed structure extractors."""

    def reconstruct(self, page_id: str, text: str) -> StructureDocument:
        """Reconstruct one page without discarding source evidence."""


@dataclass(frozen=True)
class CallableStructureAdapter:
    """Adapt a pure reconstruction callable to the structure contract."""

    runner: Callable[[str, str], StructureDocument]

    def reconstruct(self, page_id: str, text: str) -> StructureDocument:
        """Run the adapter and reject output for the wrong page."""
        result = self.runner(page_id, text)
        if result.page_id != page_id:
            raise ValueError("structure adapter returned a different page_id")
        return result


def reconstruct_structure(page_id: str, text: str) -> StructureDocument:
    """Extract deterministic hierarchy, speakers, links, and review items.

    The parser is intentionally conservative: unrecognized lines are retained as
    no assertions, while ambiguous speaker labels are abstained and queued.
    Every emitted assertion points back to the exact source line.
    """
    if not page_id:
        raise ValueError("page_id must not be empty")
    lines = list(_iter_lines(text))
    nodes: list[ParliamentaryNode] = []
    speakers: list[SpeakerAttribution] = []
    links: list[SemanticLink] = []
    review_queue: list[ReviewItem] = []
    page_span = _span(page_id, "page", 0, text) if text else None
    page = ParliamentaryNode(
        node_id=_node_id(page_id, "page", 0),
        node_type="page",
        label=page_id,
        sequence=0,
        source_spans=(page_span,) if page_span else (),
    )
    nodes.append(page)
    current_parent = page.node_id
    current_session = page.node_id
    current_sitting = page.node_id

    for sequence, (_line_number, start, line) in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        node_type = _classify_heading(stripped)
        speaker_match = _SPEAKER_PATTERN.match(stripped)
        if speaker_match and node_type is None:
            node = _make_node(page_id, "speech", stripped, sequence, current_parent, start, line)
            nodes.append(node)
            label = speaker_match.group("label").strip()
            body = speaker_match.group("body")
            attribution = _attribution(node, label)
            speakers.append(attribution)
            if attribution.abstained:
                review_queue.append(
                    ReviewItem(
                        item_id=_review_id(node.node_id, "speaker"),
                        kind="speaker_attribution",
                        reason="speaker label is generic or lacks a stable identity",
                        source_spans=attribution.source_spans,
                        candidate_ids=(),
                    )
                )
            body_offset = line.find(body)
            if body_offset >= 0:
                links.extend(_extract_links(node, body, start + body_offset, page_id))
            continue
        if node_type is None:
            continue
        parent_id = current_parent
        if node_type == "session":
            parent_id = page.node_id
        elif node_type == "sitting":
            parent_id = current_session
        elif node_type in {"date", "debate", "question", "appendix"}:
            parent_id = current_sitting
        else:
            parent_id = current_sitting
        node = _make_node(page_id, node_type, stripped, sequence, parent_id, start, line)
        nodes.append(node)
        if node_type == "session":
            current_session = node.node_id
            current_sitting = node.node_id
        elif node_type == "sitting":
            current_sitting = node.node_id
        if node_type in {"session", "sitting", "debate", "question", "appendix"}:
            current_parent = node.node_id
        elif node_type in {"date", "division", "table"}:
            current_parent = node.parent_id or current_sitting

    return StructureDocument(
        page_id=page_id,
        nodes=tuple(nodes),
        speakers=tuple(speakers),
        links=tuple(links),
        review_queue=tuple(review_queue),
    )


def export_structure_jsonld(document: StructureDocument) -> dict[str, object]:
    """Export structure assertions and links as deterministic JSON-LD."""
    nodes: list[dict[str, object]] = []
    for node in document.nodes:
        nodes.append(
            {
                "@id": f"urn:hathi:{document.page_id}:{node.node_id}",
                "@type": f"hathi:{node.node_type}",
                "label": node.label,
                "pageId": document.page_id,
                "parentId": node.parent_id,
                "sourceSpan": [span.model_dump(mode="json") for span in node.source_spans],
                "confidence": node.confidence,
                "reviewRequired": node.review_required,
            }
        )
    for index, link in enumerate(document.links):
        nodes.append(
            {
                "@id": f"urn:hathi:{document.page_id}:link-{index}",
                "@type": "hathi:semanticLink",
                "subjectId": link.subject_id,
                "relation": link.relation,
                "targetText": link.target_text,
                "targetId": link.target_id,
                "sourceSpan": [span.model_dump(mode="json") for span in link.source_spans],
                "confidence": link.confidence,
                "reviewRequired": link.review_required,
            }
        )
    for index, speaker in enumerate(document.speakers):
        nodes.append(
            {
                "@id": f"urn:hathi:{document.page_id}:speaker-{index}",
                "@type": "hathi:speakerAttribution",
                "speechNodeId": speaker.speech_node_id,
                "surfaceForm": speaker.surface_form,
                "identityId": speaker.identity_id,
                "canonicalName": speaker.canonical_name,
                "role": speaker.role,
                "validFrom": speaker.valid_from,
                "validTo": speaker.valid_to,
                "abstained": speaker.abstained,
                "sourceSpan": [span.model_dump(mode="json") for span in speaker.source_spans],
            }
        )
    for index, review in enumerate(document.review_queue):
        nodes.append(
            {
                "@id": f"urn:hathi:{document.page_id}:review-{index}",
                "@type": "hathi:reviewItem",
                "itemId": review.item_id,
                "kind": review.kind,
                "reason": review.reason,
                "candidateIds": review.candidate_ids,
                "sourceSpan": [span.model_dump(mode="json") for span in review.source_spans],
            }
        )
    return {
        "@context": {
            "hathi": "https://example.org/hathi-nz/structure#",
            "sourceSpan": "https://schema.org/hasPart",
        },
        "@graph": nodes,
        "pageId": document.page_id,
    }


def _iter_lines(text: str) -> Iterator[tuple[int, int, str]]:
    offset = 0
    for line_number, raw_line in enumerate(text.splitlines(keepends=True)):
        line = raw_line.rstrip("\r\n")
        yield line_number, offset, line
        offset += len(raw_line)
    if text and not text.endswith(("\n", "\r")) and not text.splitlines(keepends=True):
        yield 0, 0, text


def _classify_heading(line: str) -> NodeType | None:  # noqa: PLR0911
    upper = line.upper()
    if upper.startswith("VOLUME "):
        return "volume"
    if upper.startswith("SESSION "):
        return "session"
    if upper.startswith("SITTING "):
        return "sitting"
    if _DATE_PATTERN.fullmatch(line):
        return "date"
    if upper.startswith(("QUESTION", "ORAL QUESTION")):
        return "question"
    if upper.startswith(("GENERAL DEBATE", "DEBATE")):
        return "debate"
    if upper.startswith("DIVISION"):
        return "division"
    if upper.startswith("TABLE"):
        return "table"
    if upper.startswith("APPENDIX"):
        return "appendix"
    if upper.startswith("INTERJECTION"):
        return "interjection"
    return None


def _make_node(
    page_id: str,
    node_type: NodeType,
    label: str,
    sequence: int,
    parent_id: str | None,
    start: int,
    line: str,
) -> ParliamentaryNode:
    return ParliamentaryNode(
        node_id=_node_id(page_id, node_type, start),
        node_type=node_type,
        label=label,
        sequence=sequence,
        parent_id=parent_id,
        source_spans=(_span(page_id, f"line-{sequence}", start, line),),
    )


def _attribution(node: ParliamentaryNode, label: str) -> SpeakerAttribution:
    normalized = _TITLE_PATTERN.sub("", label).strip()
    generic = normalized.casefold() in {
        "member",
        "the member",
        "speaker",
        "mr speaker",
        "madam speaker",
    }
    role_match = _TITLE_PATTERN.match(label)
    role = role_match.group("title") if role_match else None
    return SpeakerAttribution(
        speech_node_id=node.node_id,
        surface_form=label,
        identity_id=None if generic else _speaker_id(normalized),
        canonical_name=None if generic else normalized,
        role=role,
        valid_from=None,
        valid_to=None,
        confidence=0.0 if generic else 0.85,
        abstained=generic,
        source_spans=node.source_spans,
    )


def _extract_links(
    node: ParliamentaryNode, body: str, body_start: int, page_id: str
) -> list[SemanticLink]:
    patterns: tuple[tuple[re.Pattern[str], LinkRelation], ...] = (
        (_LEGISLATION_PATTERN, "cites_legislation"),
        (_AGENCY_PATTERN, "mentions_agency"),
        (_PLACE_PATTERN, "mentions_place"),
        (_IWI_PATTERN, "mentions_iwi"),
        (_COMMITTEE_PATTERN, "references_committee"),
        (_PETITION_PATTERN, "references_petition"),
        (_PUBLICATION_PATTERN, "cites_publication"),
    )
    links: list[SemanticLink] = []
    for pattern, relation in patterns:
        for match in pattern.finditer(body):
            target = match.group("target").strip()
            absolute_start = body_start + match.start("target")
            source_span = _span(page_id, node.source_spans[0].block_id, absolute_start, target)
            links.append(
                SemanticLink(
                    subject_id=node.node_id,
                    relation=relation,
                    target_text=target,
                    confidence=0.75,
                    source_spans=(source_span,),
                    review_required=True,
                )
            )
    return links


def _span(page_id: str, block_id: str, start: int, text: str) -> SourceSpan:
    return SourceSpan(
        page_id=page_id, block_id=block_id, start=start, end=start + len(text), text=text
    )


def _node_id(page_id: str, node_type: str, start: int) -> str:
    return f"{node_type}-{_digest(f'{page_id}:{node_type}:{start}')}"


def _speaker_id(name: str) -> str:
    return f"person-{_digest(name.casefold())}"


def _review_id(node_id: str, kind: str) -> str:
    return f"review-{_digest(f'{node_id}:{kind}')}"


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


__all__ = [
    "CallableStructureAdapter",
    "OCRAlternative",
    "ParliamentaryNode",
    "ReviewItem",
    "SemanticLink",
    "SourceSpan",
    "SpeakerAttribution",
    "StructureAdapter",
    "StructureDocument",
    "export_structure_jsonld",
    "reconstruct_structure",
]
