"""Named entity resolution against the local NZ Wikidata knowledge base."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, TypedDict

from spacy.language import Language
from spacy.tokens import Doc

from nlp_policy_nz.kb.nz_entities import EntityContext, EntityRecord, default_nz_entities

if not Doc.has_extension("resolved_entities"):
    Doc.set_extension("resolved_entities", default=[])


@dataclass(frozen=True)
class ResolvedEntity:
    """A span resolved to one KB entity."""

    entity_id: str
    name: str
    entity_type: str
    qid: str
    start: int
    end: int
    text: str
    confidence: float
    context: dict[str, str] | None

    def to_dict(self) -> dict[str, str | int | float | dict[str, str] | None]:
        """Return a schema-safe resolved entity annotation."""
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "qid": self.qid,
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "confidence": self.confidence,
            "context": self.context,
        }


class ResolutionBenchmarkCase(TypedDict, total=False):
    """One labelled resolver precision benchmark case."""

    text: str
    span: str
    expected_entity_id: str
    party: str
    electorate: str
    date: str


class EntityResolver:
    """Resolve named spans to local KB entries with fuzzy/context scoring."""

    def __init__(
        self,
        entities: tuple[EntityRecord, ...] | list[EntityRecord] | None = None,
        *,
        min_confidence: float = 0.82,
    ) -> None:
        """Create an entity resolver."""
        self.entities = tuple(entities or default_nz_entities())
        self.min_confidence = min_confidence
        seen: set[str] = set()
        for entity in self.entities:
            if entity.entity_id in seen:
                raise ValueError(f"Duplicate entity_id in KB: {entity.entity_id}")
            seen.add(entity.entity_id)

    def resolve_one(
        self,
        span_text: str,
        *,
        context: EntityContext | None = None,
    ) -> ResolvedEntity | None:
        """Resolve one entity span."""
        scored = [(_score_entity(span_text, entity, context), entity) for entity in self.entities]
        confidence, entity = max(scored, key=lambda item: item[0])
        if confidence < self.min_confidence:
            return None
        return _resolved_entity(
            entity=entity,
            text=span_text,
            start=0,
            end=len(span_text),
            confidence=confidence,
            context=context,
        )

    def resolve_text(
        self,
        text: str,
        *,
        context: EntityContext | None = None,
    ) -> list[ResolvedEntity]:
        """Resolve all known aliases found in *text*."""
        candidates: list[ResolvedEntity] = []
        for entity in self.entities:
            for name in sorted(entity.names(), key=len, reverse=True):
                pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
                for match in pattern.finditer(text):
                    confidence = _score_entity(match.group(0), entity, context)
                    if confidence >= self.min_confidence:
                        candidates.append(
                            _resolved_entity(
                                entity=entity,
                                text=match.group(0),
                                start=match.start(),
                                end=match.end(),
                                confidence=confidence,
                                context=context,
                            )
                        )
        return _deduplicate_overlaps(candidates)


class NzEntityResolverComponent:
    """spaCy component that links document entity spans to the NZ KB."""

    def __init__(self, *, min_confidence: float = 0.82) -> None:
        """Create the resolver component."""
        self.resolver = EntityResolver(min_confidence=min_confidence)

    def __call__(self, doc: Doc) -> Doc:
        """Attach resolved entity dictionaries to ``doc._.resolved_entities``."""
        doc._.resolved_entities = [entity.to_dict() for entity in self.resolve_doc(doc)]
        return doc

    def resolve_doc(
        self,
        doc: Doc,
        *,
        context: EntityContext | None = None,
    ) -> list[ResolvedEntity]:
        """Resolve spaCy ``doc.ents`` and supplement with KB alias matches."""
        candidates: list[ResolvedEntity] = []
        for span in doc.ents:
            match = self.resolver.resolve_one(span.text, context=context)
            if match is None:
                continue
            entity = _entity_by_id(self.resolver.entities, match.entity_id)
            candidates.append(
                _resolved_entity(
                    entity=entity,
                    text=span.text,
                    start=span.start_char,
                    end=span.end_char,
                    confidence=match.confidence,
                    context=context,
                )
            )
        candidates.extend(self.resolver.resolve_text(doc.text, context=context))
        return _deduplicate_overlaps(candidates)


@Language.factory("nz_entity_resolver", default_config={"min_confidence": 0.82})
def create_nz_entity_resolver(
    nlp: Language,  # noqa: ARG001
    name: str,  # noqa: ARG001
    min_confidence: float,
) -> NzEntityResolverComponent:
    """Create the spaCy NZ entity resolver component."""
    return NzEntityResolverComponent(min_confidence=min_confidence)


def resolve_entities_in_text(
    text: str,
    *,
    entities: tuple[EntityRecord, ...] | list[EntityRecord] | None = None,
    context: EntityContext | None = None,
) -> list[dict[str, Any]]:
    """Resolve entities in *text* and return serialisable dictionaries."""
    resolver = EntityResolver(entities)
    return [entity.to_dict() for entity in resolver.resolve_text(text, context=context)]


def evaluate_resolution_precision(
    cases: list[ResolutionBenchmarkCase],
    *,
    resolver: EntityResolver | None = None,
) -> float:
    """Evaluate exact entity-id precision over labelled span cases."""
    active_resolver = resolver or EntityResolver()
    correct = 0
    for case in cases:
        context = EntityContext(
            party=case.get("party"),
            electorate=case.get("electorate"),
            date=case.get("date"),
        )
        result = active_resolver.resolve_one(case["span"], context=context)
        if result is not None and result.entity_id == case["expected_entity_id"]:
            correct += 1
    return correct / len(cases) if cases else 0.0


def _resolved_entity(
    *,
    entity: EntityRecord,
    text: str,
    start: int,
    end: int,
    confidence: float,
    context: EntityContext | None,
) -> ResolvedEntity:
    """Build a resolved entity object."""
    context_dict = context.to_dict() if context else None
    return ResolvedEntity(
        entity_id=entity.entity_id,
        name=entity.name,
        entity_type=entity.entity_type,
        qid=entity.qid,
        start=start,
        end=end,
        text=text,
        confidence=round(confidence, 3),
        context=context_dict or None,
    )


def _score_entity(
    span_text: str,
    entity: EntityRecord,
    context: EntityContext | None,
) -> float:
    """Score a span against one entity using aliases and context."""
    text = span_text.casefold()
    best = max(SequenceMatcher(None, text, name.casefold()).ratio() for name in entity.names())
    if context is not None:
        if context.party and entity.party and context.party.casefold() == entity.party.casefold():
            best += 0.05
        if (
            context.electorate
            and entity.electorate
            and context.electorate.casefold() == entity.electorate.casefold()
        ):
            best += 0.05
        if context.date and (entity.start_date or entity.end_date):
            best += 0.05 if _date_in_range(context.date, entity) else -0.2
    return min(best, 1.0)


def _date_in_range(date: str, entity: EntityRecord) -> bool:
    """Return whether a YYYY-MM-DD date is within an entity's active range."""
    if entity.start_date and date < entity.start_date:
        return False
    return not (entity.end_date and date > entity.end_date)


def _entity_by_id(entities: tuple[EntityRecord, ...], entity_id: str) -> EntityRecord:
    """Look up a KB entity by stable ID."""
    for entity in entities:
        if entity.entity_id == entity_id:
            return entity
    msg = f"Resolved entity missing from KB: {entity_id}"
    raise ValueError(msg)


def _deduplicate_overlaps(candidates: list[ResolvedEntity]) -> list[ResolvedEntity]:
    """Keep the highest-confidence non-overlapping candidate spans."""
    accepted: list[ResolvedEntity] = []
    for candidate in sorted(
        candidates, key=lambda item: (item.start, -item.confidence, -len(item.text))
    ):
        if any(candidate.start < item.end and candidate.end > item.start for item in accepted):
            continue
        accepted.append(candidate)
    return accepted
