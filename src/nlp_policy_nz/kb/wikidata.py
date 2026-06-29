"""Wikidata enrichment helpers for Track 12 entity resolution."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Protocol

from nlp_policy_nz.kb.sparql_cache import JsonSparqlCache
from nlp_policy_nz.kb.wikidata_kg import WikidataSparqlClient

if TYPE_CHECKING:
    from pathlib import Path

    from nlp_policy_nz.kb.nz_entities import EntityRecord


class WikidataPropertyClient(Protocol):
    """Protocol for QID property clients."""

    def fetch_properties(self, qid: str) -> dict[str, object]:
        """Fetch Wikidata attributes for one QID."""


class WikidataEnricher:
    """Enrich local KB entries with cached Wikidata properties."""

    def __init__(
        self,
        *,
        cache_path: str | Path = ".wikidata-entity-cache.json",
        client: WikidataPropertyClient | None = None,
    ) -> None:
        """Create a cached Wikidata enricher."""
        self.cache = JsonSparqlCache(cache_path)
        self.client = client or WikidataSparqlClient()

    def enrich(self, entity: EntityRecord) -> EntityRecord:
        """Return *entity* with additional cached Wikidata attributes."""
        cached = self.cache.get(entity.qid)
        if cached is None:
            cached = self.client.fetch_properties(entity.qid)
            self.cache.set(entity.qid, cached)
        return replace(entity, attributes={**entity.attributes, **cached})
