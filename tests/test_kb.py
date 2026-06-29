"""Tests for Track 12 named entity resolution and Wikidata linking."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import spacy

from nlp_policy_nz.kb import (
    EntityResolver,
    WikidataEnricher,
    default_nz_entities,
    evaluate_resolution_precision,
    load_nz_entities,
    resolve_entities_in_text,
)
from nlp_policy_nz.kb.nz_entities import EntityContext, EntityRecord
from nlp_policy_nz.pipeline_api import _infer_entity_context, _valid_context_date
from nlp_policy_nz.storage import PipelineRecord, load_from_parquet, serialize_to_parquet


class FakeWikidataClient:
    """Deterministic stand-in for Wikidata property lookups."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def fetch_properties(self, qid: str) -> dict[str, object]:
        """Return a fixed enrichment payload."""
        self.calls.append(qid)
        return {"source": "fake-wikidata", "qid": qid}


def test_default_kb_contains_required_entity_types_and_qids() -> None:
    """The bundled seed KB covers Track 12 entity classes."""
    entities = default_nz_entities()
    entity_types = {entity.entity_type for entity in entities}
    counts = {
        entity_type: sum(entity.entity_type == entity_type for entity in entities)
        for entity_type in entity_types
    }

    assert {"mp", "party", "electorate", "ministry", "court"} <= entity_types
    assert all(entity.qid.startswith("Q") for entity in entities)
    assert counts["mp"] >= 200
    assert counts["party"] >= 6
    assert counts["electorate"] >= 72
    assert any(entity.name == "Jacinda Ardern" for entity in entities)


def test_bundled_kb_snapshot_loads_from_json() -> None:
    """The checked-in Wikidata snapshot is loadable and has stable IDs."""
    entities = load_nz_entities(Path("data/kb/nz_entities.json"))
    by_id = {entity.entity_id: entity for entity in entities}

    assert by_id["mp:jacinda-ardern"].qid.startswith("Q")
    assert by_id["mp:christopher-luxon"].party == "New Zealand National Party"
    assert by_id["party:new-zealand-labour-party"].qid.startswith("Q")
    assert by_id["court:supreme-court-of-new-zealand"].entity_type == "court"


def test_entity_resolver_links_aliases_with_context_disambiguation() -> None:
    """Resolver should use aliases and party/electorate context to rank matches."""
    resolver = EntityResolver(default_nz_entities())
    context = EntityContext(party="Labour", electorate="Mount Albert", date="2020-10-17")

    result = resolver.resolve_one("Ardern", context=context)

    assert result is not None
    assert result.name == "Jacinda Ardern"
    assert result.entity_type == "mp"
    assert result.confidence >= 0.85
    assert result.context is not None
    assert result.context["party"] == "Labour"


def test_entity_resolver_uses_date_range_context() -> None:
    """Date context should prefer entities active on the supplied date."""
    old_member = EntityRecord(
        entity_id="mp:alex-smith-old",
        name="Alex Smith",
        entity_type="mp",
        qid="Q1",
        aliases=("Smith",),
        start_date="1990-01-01",
        end_date="1999-12-31",
    )
    current_member = EntityRecord(
        entity_id="mp:alex-smith-current",
        name="Alex Smith",
        entity_type="mp",
        qid="Q2",
        aliases=("Smith",),
        start_date="2020-01-01",
    )
    resolver = EntityResolver([old_member, current_member])

    result = resolver.resolve_one("Smith", context=EntityContext(date="2024-01-01"))

    assert result is not None
    assert result.entity_id == "mp:alex-smith-current"


def test_entity_resolver_extracts_multiple_entities_from_text() -> None:
    """Text resolution returns span-aware records suitable for PipelineRecord."""
    resolver = EntityResolver(default_nz_entities())
    text = "Jacinda Ardern spoke for Labour in Mount Albert before the Supreme Court of New Zealand."

    results = resolver.resolve_text(text)

    names = {result.name for result in results}
    assert {"Jacinda Ardern", "New Zealand Labour Party", "Mount Albert", "Supreme Court of New Zealand"} <= names
    assert all(result.start >= 0 and result.end > result.start for result in results)


def test_spacy_component_links_ner_spans_with_context() -> None:
    """spaCy component should expose resolved entities from doc spans."""
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns([{"label": "PERSON", "pattern": "Luxon"}])
    nlp.add_pipe("nz_entity_resolver")
    doc = nlp("Luxon addressed Botany for the National Party.")
    component = nlp.get_pipe("nz_entity_resolver")
    context = EntityContext(
        party="New Zealand National Party",
        electorate="Botany",
        date="2024-01-01",
    )

    resolved = component.resolve_doc(doc, context=context)

    assert any(entity.entity_id == "mp:christopher-luxon" for entity in resolved)
    assert any(item["entity_id"] == "mp:christopher-luxon" for item in doc._.resolved_entities)


def test_resolve_entities_in_text_returns_schema_safe_dicts() -> None:
    """Convenience helper emits serialisable resolved entity dictionaries."""
    resolved = resolve_entities_in_text(
        "The Ministry of Justice briefed the National Party.",
        entities=default_nz_entities(),
    )

    by_name = {item["name"]: item for item in resolved}
    assert by_name["Ministry of Justice"]["qid"].startswith("Q")
    assert by_name["New Zealand National Party"]["entity_type"] == "party"


def test_entity_resolution_benchmark_exceeds_precision_threshold() -> None:
    """Track 12 labelled benchmark must exceed the >85% precision criterion."""
    cases = json.loads(Path("tests/fixtures/kb_resolution_benchmark.json").read_text(encoding="utf-8"))

    precision = evaluate_resolution_precision(cases)

    assert precision >= 0.85


def test_resolution_precision_counts_unresolved_cases() -> None:
    """Unresolved benchmark cases count against precision."""
    precision = evaluate_resolution_precision(
        [{"span": "Not a known entity", "expected_entity_id": "mp:no-such-person"}],
        resolver=EntityResolver(default_nz_entities()),
    )

    assert precision == 0.0


def test_pipeline_entity_context_infers_party_electorate_and_date() -> None:
    """Pipeline helper should pass inferred context into entity resolution."""
    context = _infer_entity_context(
        "Luxon addressed Botany for the National Party.",
        date=_valid_context_date("2024-01-01"),
    )

    assert context.party == "New Zealand National Party"
    assert context.electorate == "Botany"
    assert context.date == "2024-01-01"


def test_wikidata_enricher_uses_cache(tmp_path: Path) -> None:
    """Wikidata enrichment should cache QID property lookups."""
    client = FakeWikidataClient()
    enricher = WikidataEnricher(cache_path=tmp_path / "wikidata-cache.json", client=client)
    entity = EntityRecord(
        entity_id="example",
        name="Example Entity",
        entity_type="party",
        qid="Q123",
    )

    first = enricher.enrich(entity)
    second = enricher.enrich(entity)

    assert first.attributes["source"] == "fake-wikidata"
    assert second.attributes["source"] == "fake-wikidata"
    assert client.calls == ["Q123"]


def test_pipeline_record_preserves_resolved_entities(tmp_path: Path) -> None:
    """Resolved entity annotations round-trip through Parquet storage."""
    record = PipelineRecord(
        doc_id="hansard-entity",
        corpus_source="hansard",
        raw_text="Jacinda Ardern spoke for Labour.",
        cleaned_tokens=["Jacinda", "Ardern", "spoke", "for", "Labour"],
        nz_act_citations=[],
        te_reo_terms=[],
        resolved_entities=resolve_entities_in_text(
            "Jacinda Ardern spoke for Labour.",
            entities=default_nz_entities(),
        ),
    )

    path = tmp_path / "entities.parquet"
    serialize_to_parquet([record], path)
    loaded = load_from_parquet(path)

    assert loaded[0].resolved_entities == record.resolved_entities


def test_resolver_rejects_duplicate_entity_ids() -> None:
    """Duplicate entity IDs are rejected to keep KB references stable."""
    duplicate = EntityRecord(entity_id="dup", name="A", entity_type="party", qid="Q1")

    with pytest.raises(ValueError, match="Duplicate entity_id"):
        EntityResolver([duplicate, duplicate])
