"""Temporal expression extraction for New Zealand legal text."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from typing import Any

import networkx as nx
from spacy.language import Language
from spacy.tokens import Doc, Token

__all__ = [
    "TEMPORAL_PATTERNS",
    "TemporalExpression",
    "TemporalExtractor",
    "TemporalGraph",
    "TemporalType",
    "detect_temporal_expressions",
]


class TemporalType(Enum):
    """TimeML-style temporal expression classes."""

    DATE = "DATE"
    TIME = "TIME"
    DURATION = "DURATION"
    SET = "SET"


@dataclass(frozen=True)
class TemporalExpression:
    """A normalized temporal expression detected in legal text."""

    timex_type: TemporalType
    text: str
    normalized: str
    start: int
    end: int
    signal: str | None = None
    role: str | None = None
    section_id: str | None = None

    def to_dict(self) -> dict[str, str | int | None]:
        """Return a serialization-friendly temporal annotation dictionary."""
        data = asdict(self)
        data["timex_type"] = self.timex_type.value
        return data


MONTHS: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

UNIT_TO_PERIOD: dict[str, str] = {
    "day": "D",
    "days": "D",
    "week": "W",
    "weeks": "W",
    "month": "M",
    "months": "M",
    "year": "Y",
    "years": "Y",
}

TEMPORAL_PATTERNS: tuple[dict[str, Any], ...] = (
    {
        "name": "written_date",
        "timex_type": TemporalType.DATE,
        "regex": re.compile(
            r"\b(?P<day>[0-3]?\d)\s+"
            r"(?P<month>January|February|March|April|May|June|July|August|"
            r"September|October|November|December)\s+"
            r"(?P<year>\d{4})\b",
            re.IGNORECASE,
        ),
    },
    {
        "name": "iso_date",
        "timex_type": TemporalType.DATE,
        "regex": re.compile(r"\b(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\b"),
    },
    {
        "name": "clock_time",
        "timex_type": TemporalType.TIME,
        "regex": re.compile(
            r"\b(?P<hour>1[0-2]|0?[1-9])(?::(?P<minute>\d{2}))?\s*(?P<ampm>am|pm)\b", re.IGNORECASE
        ),
    },
    {
        "name": "duration",
        "timex_type": TemporalType.DURATION,
        "regex": re.compile(
            r"\b(?P<signal>within|for|after|before|not later than)\s+"
            r"(?P<count>\d+)\s+(?P<unit>days?|weeks?|months?|years?)\b",
            re.IGNORECASE,
        ),
    },
    {
        "name": "recurrence",
        "timex_type": TemporalType.SET,
        "regex": re.compile(
            r"\b(?P<signal>every)\s+(?P<count>\d+)\s+"
            r"(?P<unit>days?|weeks?|months?|years?)\b",
            re.IGNORECASE,
        ),
    },
    {
        "name": "named_recurrence",
        "timex_type": TemporalType.SET,
        "regex": re.compile(r"\b(?P<named>annually|yearly|monthly|weekly|daily)\b", re.IGNORECASE),
    },
)
"""Ordered temporal expression patterns for NZ legislation and Hansard text."""


def _ensure_extensions() -> None:
    """Register spaCy extensions used by the temporal extractor."""
    if not Token.has_extension("temporal_expression"):
        Token.set_extension("temporal_expression", default=None)
    if not Doc.has_extension("temporal_expressions"):
        Doc.set_extension("temporal_expressions", default=None)


_ensure_extensions()


@Language.factory("temporal_extractor", default_config={"patterns": None})
class TemporalExtractor:
    """spaCy component that extracts normalized temporal expressions."""

    def __init__(
        self,
        nlp: Language,
        name: str = "temporal_extractor",
        patterns: tuple[dict[str, Any], ...] | None = None,
    ) -> None:
        """Initialize the instance."""
        self.name = name
        self.vocab = nlp.vocab
        self.patterns = patterns if patterns is not None else TEMPORAL_PATTERNS

    def __call__(self, doc: Doc) -> Doc:
        """Annotate temporal expressions on a spaCy document."""
        annotations = self.extract(doc.text)
        for annotation in annotations:
            for token in doc:
                if token.idx >= annotation.start and token.idx < annotation.end:
                    token._.temporal_expression = annotation
        doc._.temporal_expressions = annotations
        return doc

    def extract(self, text: str) -> list[TemporalExpression]:
        """Extract temporal expressions from *text*."""
        annotations: list[TemporalExpression] = []
        occupied: list[tuple[int, int]] = []

        for pattern in self.patterns:
            timex_type = pattern["timex_type"]
            regex: re.Pattern[str] = pattern["regex"]
            for match in regex.finditer(text):
                span = match.span()
                if _overlaps(span, occupied):
                    continue
                normalized = _normalize_match(timex_type, match)
                if normalized is None:
                    continue
                signal = match.groupdict().get("signal")
                annotation = TemporalExpression(
                    timex_type=timex_type,
                    text=match.group(0),
                    normalized=normalized,
                    start=match.start(),
                    end=match.end(),
                    signal=signal.lower() if signal else _nearby_signal(text, match.start()),
                    role=_classify_role(text, match.start(), match.end(), timex_type),
                    section_id=_nearby_section_id(text, match.start()),
                )
                annotations.append(annotation)
                occupied.append(span)

        return sorted(annotations, key=lambda annotation: annotation.start)

    def to_disk(self, _path: str, **_kwargs: object) -> None:
        """Serialize the component.

        Patterns are code-defined, so there is no on-disk state.
        """

    def from_disk(self, _path: str, **_kwargs: object) -> TemporalExtractor:
        """Deserialize the component and return ``self``."""
        return self


class TemporalGraph:
    """Small section-to-time graph for legal effective-period queries."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.graph: nx.DiGraph = nx.DiGraph()

    def add_section(self, section_id: str, title: str | None = None) -> None:
        """Register a legal section node."""
        if not self.graph.has_node(section_id):
            self.graph.add_node(
                section_id,
                node_type="section",
                title=title,
                start=None,
                end=None,
            )
        elif title is not None:
            self.graph.nodes[section_id]["title"] = title

    def link_temporal_expression(
        self,
        section_id: str,
        expression: TemporalExpression,
    ) -> None:
        """Attach a temporal expression to a section and infer effective bounds."""
        self.add_section(section_id)
        expression_id = f"time:{section_id}:{expression.normalized}"
        duplicate = sum(
            1
            for _source, target in self.graph.out_edges(section_id)
            if target.startswith(expression_id)
        )
        if duplicate:
            expression_id = f"{expression_id}:{duplicate}"
        self.graph.add_node(
            expression_id,
            node_type="temporal_expression",
            timex_type=expression.timex_type.value,
            text=expression.text,
            normalized=expression.normalized,
            signal=expression.signal,
            role=expression.role,
            section_id=expression.section_id,
        )
        self.graph.add_edge(
            section_id,
            expression_id,
            relation=expression.role or "temporal_reference",
        )
        if expression.timex_type is not TemporalType.DATE:
            return

        if expression.role in {"commencement", "effective"}:
            self.graph.nodes[section_id]["start"] = expression.normalized
        elif expression.role in {"expiry", "deadline"}:
            self.graph.nodes[section_id]["end"] = expression.normalized

    def add_effective_period(
        self,
        section_id: str,
        start: str | None,
        end: str | None = None,
    ) -> None:
        """Set a section's explicit ISO date effective period."""
        self.add_section(section_id)
        self.graph.nodes[section_id]["start"] = start
        self.graph.nodes[section_id]["end"] = end

    def effective_period(self, section_id: str) -> tuple[str | None, str | None]:
        """Return the effective start and end dates for *section_id*."""
        if not self.graph.has_node(section_id):
            return (None, None)
        section = self.graph.nodes[section_id]
        return (section.get("start"), section.get("end"))

    def find_active_sections(self, on_date: str) -> list[str]:
        """Return sections active on the given ISO date."""
        active: list[str] = []
        for section_id, section in self.graph.nodes(data=True):
            if section.get("node_type") != "section":
                continue
            start = section.get("start")
            end = section.get("end")
            if start is not None and on_date < start:
                continue
            if end is not None and on_date > end:
                continue
            if start is not None or end is not None:
                active.append(section_id)
        return active


def detect_temporal_expressions(text: str, nlp: Language) -> list[TemporalExpression]:
    """Detect normalized temporal expressions in *text* using *nlp*."""
    if "temporal_extractor" not in nlp.pipe_names:
        nlp.add_pipe("temporal_extractor", last=True)
    doc = nlp(text)
    annotations = doc._.temporal_expressions
    return list(annotations or [])


def _overlaps(span: tuple[int, int], occupied: list[tuple[int, int]]) -> bool:
    """Return whether *span* overlaps any accepted annotation span."""
    start, end = span
    return any(
        start < accepted_end and end > accepted_start for accepted_start, accepted_end in occupied
    )


def _normalize_match(timex_type: TemporalType, match: re.Match[str]) -> str | None:
    """Normalize a regex match to an ISO 8601 date, time, duration, or recurrence."""
    groups = match.groupdict()
    if timex_type is TemporalType.DATE:
        return _date_value(groups["year"], groups["month"], groups["day"])

    if timex_type is TemporalType.TIME:
        hour = int(groups["hour"])
        minute = int(groups.get("minute") or 0)
        ampm = groups["ampm"].lower()
        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute:02d}"

    if timex_type is TemporalType.DURATION:
        return _duration_value(groups["count"], groups["unit"])

    if timex_type is TemporalType.SET:
        named = groups.get("named")
        if named:
            return {
                "annually": "P1Y",
                "yearly": "P1Y",
                "monthly": "P1M",
                "weekly": "P1W",
                "daily": "P1D",
            }[named.lower()]
        return _duration_value(groups["count"], groups["unit"])

    return None


def _date_value(year_value: str, month_value: str, day_value: str) -> str | None:
    """Return a validated ISO 8601 calendar date, or ``None`` for invalid input."""
    day = int(day_value)
    month = int(month_value) if month_value.isdigit() else MONTHS[month_value.lower()]
    year = int(year_value)
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _duration_value(count: str, unit: str) -> str:
    """Return an ISO 8601 duration value for count and legal time unit."""
    return f"P{int(count)}{UNIT_TO_PERIOD[unit.lower()]}"


def _nearby_signal(text: str, start: int) -> str | None:
    """Return a short temporal signal preceding an expression, if present."""
    prefix = text[max(0, start - 18) : start].lower()
    match = re.search(r"\b(on|at|from|until|before|after)\s+$", prefix)
    return match.group(1) if match else None


def _classify_role(text: str, start: int, end: int, timex_type: TemporalType) -> str | None:
    """Classify the legal temporal role from local context."""
    context = text[max(0, start - 80) : min(len(text), end + 80)].lower()
    matched = text[start:end].lower()
    role_checks: tuple[tuple[str, bool], ...] = (
        (
            "deadline",
            timex_type is TemporalType.DURATION
            and (
                any(term in context for term in ("deadline", "not later than", "within"))
                or matched.startswith("within")
            ),
        ),
        (
            "commencement",
            any(term in context for term in ("commence", "comes into force", "commencement")),
        ),
        ("expiry", any(term in context for term in ("expires", "ceases", "until"))),
        (
            "deadline",
            any(term in context for term in ("deadline", "not later than", "within"))
            or matched.startswith("within"),
        ),
        ("effective", any(term in context for term in ("effective", "in force"))),
    )
    if timex_type is TemporalType.SET:
        return "recurrence"
    for role, matched_role in role_checks:
        if matched_role:
            return role
    return None


def _nearby_section_id(text: str, start: int) -> str | None:
    """Infer a nearby section identifier from preceding legal text."""
    prefix = text[max(0, start - 80) : start]
    matches = list(
        re.finditer(r"\b(?:section|s)\s+(?P<section>\d+[A-Za-z]?)\b", prefix, re.IGNORECASE)
    )
    if not matches:
        return None
    return f"s{matches[-1].group('section')}"
