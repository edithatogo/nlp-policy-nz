"""Wikidata ontology mapping, resolution, enrichment, and JSON-LD export."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Protocol

import requests
from rdflib import Graph

from nlp_policy_nz.kb.sparql_cache import JsonSparqlCache

WIKIDATA_ONTOLOGY_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "ontologies" / "nz_wikidata_map.ttl"
)
WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
WIKIDATA_ENTITY_URI = "https://www.wikidata.org/entity/"
LOCAL_ONTOLOGY_URI = "https://legal-nz.example.org/ontology/"

ENTITY_CLASS_QIDS: dict[str, str] = {
    "act": "Q820655",
    "mp": "Q486839",
    "party": "Q7278",
    "electorate": "Q192611",
    "court": "Q41487",
}
SCHEMA_TYPES: dict[str, str] = {
    "act": "schema:Legislation",
    "mp": "schema:Person",
    "party": "schema:Organization",
    "electorate": "schema:AdministrativeArea",
    "court": "schema:Courthouse",
}


class EntitySearchClient(Protocol):
    """Protocol for QID search clients."""

    def search_entity(self, name: str, entity_type: str) -> dict[str, Any] | None:
        """Resolve an entity name and type to Wikidata metadata."""


class EntityPropertyClient(Protocol):
    """Protocol for Wikidata property enrichment clients."""

    def fetch_properties(self, qid: str) -> dict[str, Any]:
        """Fetch selected Wikidata properties for a QID."""


@dataclass(frozen=True)
class WikidataEntity:
    """Resolved local entity annotated with a Wikidata QID."""

    name: str
    entity_type: str
    qid: str | None = None
    label: str | None = None
    description: str | None = None
    match_score: float = 0.0
    wikidata_url: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> WikidataEntity:
        """Build an entity from JSON-compatible mapping data."""
        qid = data.get("qid")
        return cls(
            name=str(data["name"]),
            entity_type=str(data["entity_type"]),
            qid=str(qid) if qid else None,
            label=str(data.get("label") or data["name"]),
            description=(str(data["description"]) if data.get("description") is not None else None),
            match_score=float(data.get("match_score", 1.0 if qid else 0.0)),
            wikidata_url=(
                str(data.get("wikidata_url") or f"{WIKIDATA_ENTITY_URI}{qid}") if qid else None
            ),
            attributes=dict(data.get("attributes") or {}),
        )


class WikidataSparqlClient:
    """Minimal Wikidata Query Service client."""

    def __init__(
        self,
        endpoint: str = WIKIDATA_SPARQL_ENDPOINT,
        *,
        timeout: int = 30,
        user_agent: str = "nlp-policy-nz/0.1",
    ) -> None:
        """Create a SPARQL client."""
        self.endpoint = endpoint
        self.timeout = timeout
        self.user_agent = user_agent

    def search_entity(self, name: str, entity_type: str) -> dict[str, Any] | None:
        """Resolve *name* to the best Wikidata QID for *entity_type*."""
        class_qid = ENTITY_CLASS_QIDS.get(entity_type)
        type_clause = f"?item wdt:P31/wdt:P279* wd:{class_qid} ." if class_qid is not None else ""
        query = f"""
        SELECT ?item ?itemLabel ?itemDescription WHERE {{
          ?item rdfs:label "{_escape_sparql_literal(name)}"@en .
          {type_clause}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 5
        """
        rows = self._query(query)
        if not rows:
            return None
        binding = rows[0]
        item = _binding_value(binding, "item")
        qid = item.rsplit("/", 1)[-1]
        label = _binding_value(binding, "itemLabel") or name
        description = _binding_value(binding, "itemDescription")
        return {
            "qid": qid,
            "label": label,
            "description": description,
            "match_score": _label_score(name, label),
            "wikidata_url": f"{WIKIDATA_ENTITY_URI}{qid}",
        }

    def fetch_properties(self, qid: str) -> dict[str, Any]:
        """Fetch selected Wikidata attributes for *qid*."""
        query = f"""
        SELECT ?inception ?partyLabel ?start ?end WHERE {{
          OPTIONAL {{ wd:{qid} wdt:P571 ?inception . }}
          OPTIONAL {{
            wd:{qid} p:P102 ?partyStatement .
            ?partyStatement ps:P102 ?party .
            OPTIONAL {{ ?partyStatement pq:P580 ?start . }}
            OPTIONAL {{ ?partyStatement pq:P582 ?end . }}
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT 25
        """
        rows = self._query(query)
        party_membership: list[dict[str, str]] = []
        inception_date: str | None = None
        for row in rows:
            inception_date = inception_date or _binding_value(row, "inception")
            party = _binding_value(row, "partyLabel")
            if party:
                party_membership.append(
                    {
                        "party": party,
                        "start": _binding_value(row, "start") or "",
                        "end": _binding_value(row, "end") or "",
                    }
                )
        data: dict[str, Any] = {}
        if inception_date:
            data["inception_date"] = inception_date
        if party_membership:
            data["party_membership"] = party_membership
        return data

    def _query(self, query: str) -> list[dict[str, Any]]:
        """Run a SPARQL query and return raw bindings."""
        response = requests.get(
            self.endpoint,
            params={"query": query, "format": "json"},
            headers={"Accept": "application/sparql-results+json", "User-Agent": self.user_agent},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        bindings = payload.get("results", {}).get("bindings", [])
        return list(bindings) if isinstance(bindings, list) else []


class WikidataResolver:
    """Resolve local entity names to Wikidata QIDs with persistent caching."""

    def __init__(
        self,
        *,
        client: EntitySearchClient | None = None,
        cache: JsonSparqlCache | None = None,
    ) -> None:
        """Create a resolver with optional client and cache overrides."""
        self.client = client or WikidataSparqlClient()
        self.cache = cache or JsonSparqlCache(Path(".wikidata-cache.json"))

    def resolve(self, name: str, *, entity_type: str) -> WikidataEntity:
        """Resolve one entity name."""
        key = _cache_key(name, entity_type)
        cached = self.cache.get(key)
        if cached is not None:
            return WikidataEntity.from_mapping(cached)

        result = self.client.search_entity(name, entity_type)
        if result is None:
            entity = WikidataEntity(name=name, entity_type=entity_type)
        else:
            entity = WikidataEntity.from_mapping(
                {
                    "name": name,
                    "entity_type": entity_type,
                    **result,
                }
            )
        self.cache.set(key, _entity_to_mapping(entity))
        return entity

    def bulk_resolve(self, names: Iterable[str], *, entity_type: str) -> list[WikidataEntity]:
        """Resolve multiple names while reusing cached duplicate lookups."""
        return [self.resolve(name, entity_type=entity_type) for name in names]


def load_ontology_graph(path: str | Path = WIKIDATA_ONTOLOGY_PATH) -> Graph:
    """Load the NZ Wikidata OWL/Turtle ontology map."""
    graph = Graph()
    graph.parse(str(path), format="turtle")
    return graph


def enrich_entities(
    entities: Sequence[WikidataEntity],
    *,
    client: EntityPropertyClient | None = None,
) -> list[WikidataEntity]:
    """Populate resolved entities with selected Wikidata attributes."""
    wikidata_client = client or WikidataSparqlClient()
    enriched: list[WikidataEntity] = []
    for entity in entities:
        if not entity.qid:
            enriched.append(entity)
            continue
        attributes = {
            **entity.attributes,
            **wikidata_client.fetch_properties(entity.qid),
        }
        enriched.append(replace(entity, attributes=attributes))
    return enriched


def export_knowledge_graph_jsonld(
    entities: Sequence[WikidataEntity],
    output_path: str | Path,
    *,
    base_uri: str = "https://legal-nz.example.org/kg/",
) -> Path:
    """Write a schema.org-compatible JSON-LD knowledge graph."""
    target = Path(output_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "@context": {
            "schema": "https://schema.org/",
            "wd": "https://www.wikidata.org/entity/",
            "nlp": LOCAL_ONTOLOGY_URI,
        },
        "@graph": [_entity_jsonld(entity, base_uri=base_uri) for entity in entities],
    }
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def load_wikidata_entities(path: str | Path) -> list[WikidataEntity]:
    """Load resolved entity records from a JSON file."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Knowledge graph entity file must contain a JSON list.")
    return [WikidataEntity.from_mapping(item) for item in payload]


def federated_sparql_query_example() -> str:
    """Return a federated SPARQL example joining local KG data to Wikidata."""
    return """
PREFIX schema: <https://schema.org/>
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?localEntity ?name ?wikidataEntity ?wikidataClass WHERE {
  ?localEntity schema:name ?name ;
               schema:sameAs ?wikidataEntity .
  SERVICE <https://query.wikidata.org/sparql> {
    ?wikidataEntity wdt:P31 ?wikidataClass .
  }
}
""".strip()


def _entity_jsonld(entity: WikidataEntity, *, base_uri: str) -> dict[str, Any]:
    """Convert one entity to schema.org JSON-LD."""
    node: dict[str, Any] = {
        "@id": _entity_uri(entity, base_uri),
        "@type": SCHEMA_TYPES.get(entity.entity_type, "schema:Thing"),
        "schema:name": entity.label or entity.name,
        "schema:identifier": entity.qid,
    }
    if entity.description:
        node["schema:description"] = entity.description
    if entity.wikidata_url:
        node["schema:sameAs"] = entity.wikidata_url
    if entity.attributes:
        node["schema:additionalProperty"] = [
            {
                "@type": "schema:PropertyValue",
                "schema:name": key,
                "schema:value": value,
            }
            for key, value in sorted(entity.attributes.items())
        ]
    return node


def _entity_uri(entity: WikidataEntity, base_uri: str) -> str:
    """Build a local URI for an entity."""
    return base_uri.rstrip("/") + f"/{entity.entity_type}/{_slug(entity.name)}"


def _slug(value: str) -> str:
    """Return a stable URI-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def _cache_key(name: str, entity_type: str) -> str:
    """Return a normalized cache key."""
    return f"{entity_type.strip().lower()}::{name.strip().casefold()}"


def _entity_to_mapping(entity: WikidataEntity) -> dict[str, Any]:
    """Convert an entity to JSON-compatible cache data."""
    return {
        "name": entity.name,
        "entity_type": entity.entity_type,
        "qid": entity.qid,
        "label": entity.label,
        "description": entity.description,
        "match_score": entity.match_score,
        "wikidata_url": entity.wikidata_url,
        "attributes": entity.attributes,
    }


def _escape_sparql_literal(value: str) -> str:
    """Escape a string for use as a SPARQL literal."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _binding_value(binding: Mapping[str, Any], key: str) -> str:
    """Extract one string value from a SPARQL JSON binding."""
    item = binding.get(key)
    if isinstance(item, Mapping):
        value = item.get("value")
        return str(value) if value is not None else ""
    return ""


def _label_score(name: str, label: str) -> float:
    """Return a deterministic precision-oriented label score."""
    return 1.0 if name.casefold() == label.casefold() else 0.9
