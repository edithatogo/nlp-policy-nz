"""Argument mining for New Zealand parliamentary debate text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal, Self

import networkx as nx

ArgumentType = Literal["premise", "conclusion", "none"]
RelationType = Literal["support", "attack"]

PREMISE_CUES: tuple[str, ...] = (
    "because",
    "since",
    "the evidence shows",
    "evidence shows",
    "given that",
    "as a result of",
    "costs will",
    "rents are",
    "emissions are",
)
CONCLUSION_CUES: tuple[str, ...] = (
    "therefore",
    "should pass",
    "should be rejected",
    "this supports",
    "must pass",
    "commend it",
    "need support",
)
ATTACK_CUES: tuple[str, ...] = (
    "however",
    "oppose",
    "reject",
    "harmful",
    "delay",
    "raises costs",
)


@dataclass(frozen=True)
class ArgumentComponent:
    """One detected argument component span."""

    component_id: str
    component_type: ArgumentType
    text: str
    start: int
    end: int
    confidence: float

    def to_dict(self) -> dict[str, str | int | float]:
        """Return a schema-safe argument component dictionary."""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class ArgumentRelation:
    """Directed relation between argument components."""

    source_id: str
    target_id: str
    relation: RelationType
    confidence: float

    def to_dict(self) -> dict[str, str | float]:
        """Return a schema-safe relation dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
            "confidence": self.confidence,
        }


class ArgumentDetector:
    """Rule-backed argument component detector for Hansard-style text."""

    def detect(self, text: str) -> list[ArgumentComponent]:
        """Detect premise and conclusion spans in text."""
        components: list[ArgumentComponent] = []
        for index, sentence in enumerate(_sentence_spans(text), start=1):
            for component_type in _classify_components(sentence.text):
                if component_type == "none":
                    continue
                components.append(
                    ArgumentComponent(
                        component_id=f"arg-{index}-{component_type}",
                        component_type=component_type,
                        text=sentence.text,
                        start=sentence.start,
                        end=sentence.end,
                        confidence=0.9,
                    )
                )
        return components


class ArgumentGraph:
    """NetworkX-backed argument graph with AIF-compatible JSON-LD export."""

    def __init__(self, *, issue: str | None = None) -> None:
        """Create an empty argument graph."""
        self.issue = issue
        self.graph: nx.DiGraph = nx.DiGraph()

    @classmethod
    def from_arguments(
        cls,
        arguments: list[ArgumentComponent],
        *,
        issue: str | None = None,
    ) -> Self:
        """Build a graph from argument components."""
        graph = cls(issue=issue)
        for argument in arguments:
            graph.add_component(argument)
        graph.add_inferred_relations(arguments)
        return graph

    def add_component(self, argument: ArgumentComponent) -> None:
        """Add an argument component node."""
        self.graph.add_node(
            argument.component_id,
            type=argument.component_type,
            text=argument.text,
            start=argument.start,
            end=argument.end,
            confidence=argument.confidence,
        )

    def add_relation(self, relation: ArgumentRelation) -> None:
        """Add a directed relation edge."""
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            relation=relation.relation,
            confidence=relation.confidence,
        )

    def add_inferred_relations(self, arguments: list[ArgumentComponent]) -> None:
        """Infer premise-to-conclusion support/attack relations."""
        conclusions = [item for item in arguments if item.component_type == "conclusion"]
        if not conclusions:
            return
        for argument in arguments:
            if argument.component_type == "conclusion":
                continue
            target = min(conclusions, key=lambda item: abs(item.start - argument.start))
            relation: RelationType = "attack" if _contains_any(argument.text, ATTACK_CUES) else "support"
            self.add_relation(
                ArgumentRelation(
                    source_id=argument.component_id,
                    target_id=target.component_id,
                    relation=relation,
                    confidence=0.85,
                )
            )

    def to_aif_jsonld(self) -> dict[str, Any]:
        """Export the graph using a compact AIF-style JSON-LD shape."""
        nodes = [
            {
                "@id": node,
                "@type": "aif:I-node",
                "id": node,
                **data,
            }
            for node, data in self.graph.nodes(data=True)
        ]
        edges = [
            {
                "@id": f"{source}-{data.get('relation', 'rel')}-{target}",
                "@type": "aif:RA" if data.get("relation") == "support" else "aif:CA",
                "source": source,
                "target": target,
                **data,
            }
            for source, target, data in self.graph.edges(data=True)
        ]
        return {
            "@context": {
                "aif": "http://www.arg.dundee.ac.uk/aif#",
                "source": {"@id": "aif:fromID"},
                "target": {"@id": "aif:toID"},
                "support": "aif:RA",
                "attack": "aif:CA",
            },
            "@type": "aif:ArgumentNetwork",
            "type": "ArgumentGraph",
            "issue": self.issue,
            "@graph": [*nodes, *edges],
            "nodes": nodes,
            "edges": edges,
        }


@dataclass(frozen=True)
class _SentenceSpan:
    text: str
    start: int
    end: int


def evaluate_argument_components(
    labelled_segments: list[dict[str, object]],
    *,
    detector: ArgumentDetector | None = None,
) -> dict[str, float]:
    """Evaluate component detection over labelled text segments."""
    active_detector = detector or ArgumentDetector()
    true_positive = 0
    false_positive = 0
    false_negative = 0
    for case in labelled_segments:
        expected = set(case["expected"])
        observed = {argument.component_type for argument in active_detector.detect(str(case["text"]))}
        if not observed:
            observed = {"none"}
        true_positive += len(expected & observed)
        false_positive += len(observed - expected)
        false_negative += len(expected - observed)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def link_arguments_to_issues(
    arguments: list[ArgumentComponent],
    issues: list[str],
) -> list[dict[str, str | float]]:
    """Link each argument to the most similar issue by token overlap."""
    links: list[dict[str, str | float]] = []
    for argument in arguments:
        ranked = sorted(
            ((_jaccard(argument.text, issue), issue) for issue in issues),
            reverse=True,
        )
        if not ranked:
            continue
        score, issue = ranked[0]
        links.append(
            {
                "component_id": argument.component_id,
                "issue": issue,
                "similarity": round(score, 3),
            }
        )
    return links


def _sentence_spans(text: str) -> list[_SentenceSpan]:
    """Split text into simple sentence spans while preserving offsets."""
    spans: list[_SentenceSpan] = []
    for match in re.finditer(r"[^.!?]+[.!?]?", text):
        sentence = match.group(0).strip()
        if not sentence:
            continue
        start = text.find(sentence, match.start())
        spans.append(_SentenceSpan(text=sentence, start=start, end=start + len(sentence)))
    return spans


def _classify_components(sentence: str) -> list[ArgumentType]:
    """Classify one sentence as one or more argument component types."""
    component_types: list[ArgumentType] = []
    if _contains_any(sentence, PREMISE_CUES) or _contains_any(sentence, ATTACK_CUES):
        component_types.append("premise")
    if _contains_any(sentence, CONCLUSION_CUES):
        component_types.append("conclusion")
    return component_types or ["none"]


def _contains_any(text: str, cues: tuple[str, ...]) -> bool:
    """Return whether text contains any cue phrase."""
    folded = text.casefold()
    return any(cue in folded for cue in cues)


def _tokens(text: str) -> set[str]:
    """Return normalized content tokens."""
    stopwords = {"the", "a", "an", "and", "or", "to", "of", "in", "for", "is", "are"}
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.casefold())
        if token not in stopwords
    }


def _jaccard(left: str, right: str) -> float:
    """Return Jaccard similarity for two strings."""
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
