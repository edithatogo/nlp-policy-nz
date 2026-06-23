"""Tests for Wikidata knowledge graph integration."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from rdflib import Graph, Namespace
from rdflib.namespace import OWL

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.kb import (
    WIKIDATA_ONTOLOGY_PATH,
    JsonSparqlCache,
    WikidataEntity,
    WikidataResolver,
    WikidataSparqlClient,
    enrich_entities,
    export_knowledge_graph_jsonld,
    federated_sparql_query_example,
    load_ontology_graph,
    load_wikidata_entities,
)

NLP = Namespace("https://legal-nz.example.org/ontology/")


class FakeWikidataClient:
    """Deterministic fake SPARQL/search client for resolver tests."""

    def __init__(self) -> None:
        self.search_calls: list[tuple[str, str]] = []
        self.property_calls: list[str] = []

    def search_entity(self, name: str, entity_type: str) -> dict[str, Any] | None:
        """Return a stable fake QID result."""
        self.search_calls.append((name, entity_type))
        qid = {
            "Act": "Q820655",
            "Jane Doe": "Q12345",
            "Example Party": "Q7278",
        }.get(name)
        if qid is None:
            return None
        return {
            "qid": qid,
            "label": name,
            "description": f"{entity_type} result",
            "match_score": 0.96,
            "wikidata_url": f"https://www.wikidata.org/entity/{qid}",
        }

    def fetch_properties(self, qid: str) -> dict[str, Any]:
        """Return deterministic enrichment data."""
        self.property_calls.append(qid)
        return {
            "inception_date": "1854-05-24",
            "party_membership": ["Example Party"],
            "source": "fake-wikidata",
        }


class FakeHttpResponse:
    """Minimal response object for mocked SPARQL HTTP calls."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.raised = False

    def raise_for_status(self) -> None:
        """Record that HTTP status validation was requested."""
        self.raised = True

    def json(self) -> dict[str, Any]:
        """Return the prepared SPARQL JSON payload."""
        return self.payload


def _case_dir(name: str) -> Path:
    """Return a workspace-local output directory."""
    path = Path("track17-test-output") / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_ontology_map_covers_required_entity_classes() -> None:
    """OWL/Turtle map covers Acts, MPs, parties, electorates, and courts."""
    graph = load_ontology_graph(WIKIDATA_ONTOLOGY_PATH)
    required = {
        NLP.NZAct,
        NLP.NZMemberOfParliament,
        NLP.NZPoliticalParty,
        NLP.NZElectorate,
        NLP.NZCourt,
    }

    for subject in required:
        assert (subject, OWL.equivalentClass, None) in graph


def test_bulk_resolver_uses_cache() -> None:
    """Bulk QID resolver caches name/type lookups."""
    cache_path = _case_dir("cache") / "wikidata-cache.json"
    client = FakeWikidataClient()
    resolver = WikidataResolver(client=client, cache=JsonSparqlCache(cache_path))

    first = resolver.bulk_resolve(["Jane Doe", "Jane Doe"], entity_type="mp")
    second = resolver.bulk_resolve(["Jane Doe"], entity_type="mp")
    unresolved = resolver.resolve("Unknown Court", entity_type="court")

    assert [entity.qid for entity in first] == ["Q12345", "Q12345"]
    assert [entity.qid for entity in second] == ["Q12345"]
    assert unresolved.qid is None
    assert client.search_calls == [("Jane Doe", "mp"), ("Unknown Court", "court")]
    assert cache_path.is_file()


def test_sparql_client_maps_search_and_property_bindings() -> None:
    """SPARQL client maps mocked Wikidata responses into stable dictionaries."""
    calls: list[dict[str, Any]] = []

    def fake_get(
        endpoint: str,
        *,
        params: dict[str, str],
        headers: dict[str, str],
        timeout: int,
    ) -> FakeHttpResponse:
        calls.append({
            "endpoint": endpoint,
            "query": params["query"],
            "headers": headers,
            "timeout": timeout,
        })
        if "itemDescription" in params["query"]:
            return FakeHttpResponse({
                "results": {
                    "bindings": [
                        {
                            "item": {"value": "https://www.wikidata.org/entity/Q123"},
                            "itemLabel": {"value": "Example Act"},
                            "itemDescription": {"value": "test statute"},
                        }
                    ]
                }
            })
        return FakeHttpResponse({
            "results": {
                "bindings": [
                    {
                        "inception": {"value": "1893-09-19T00:00:00Z"},
                        "partyLabel": {"value": "Example Party"},
                        "start": {"value": "2020-10-17T00:00:00Z"},
                    }
                ]
            }
        })

    with patch("nlp_policy_nz.kb.wikidata_kg.requests.get", side_effect=fake_get):
        client = WikidataSparqlClient(
            endpoint="https://example.test/sparql",
            timeout=7,
            user_agent="test-agent",
        )
        result = client.search_entity('Example "Act"', "act")
        properties = client.fetch_properties("Q123")

    assert result == {
        "qid": "Q123",
        "label": "Example Act",
        "description": "test statute",
        "match_score": 0.9,
        "wikidata_url": "https://www.wikidata.org/entity/Q123",
    }
    assert properties["inception_date"] == "1893-09-19T00:00:00Z"
    assert properties["party_membership"] == [
        {
            "party": "Example Party",
            "start": "2020-10-17T00:00:00Z",
            "end": "",
        }
    ]
    assert calls[0]["endpoint"] == "https://example.test/sparql"
    assert calls[0]["headers"]["User-Agent"] == "test-agent"
    assert '\\"Act\\"' in calls[0]["query"]
    assert calls[0]["timeout"] == 7


def test_sparql_client_handles_empty_or_malformed_results() -> None:
    """SPARQL client returns empty results for malformed binding payloads."""

    def fake_get(
        _endpoint: str,
        *,
        params: dict[str, str],
        headers: dict[str, str],
        timeout: int,
    ) -> FakeHttpResponse:
        assert params["format"] == "json"
        assert headers["Accept"] == "application/sparql-results+json"
        assert timeout == 30
        return FakeHttpResponse({"results": {"bindings": {}}})

    with patch("nlp_policy_nz.kb.wikidata_kg.requests.get", side_effect=fake_get):
        client = WikidataSparqlClient()

        assert client.search_entity("Missing", "untyped") is None
        assert client.fetch_properties("Q0") == {}


def test_property_enrichment_adds_wikidata_attributes() -> None:
    """Property enrichment preserves entities and adds Wikidata attributes."""
    client = FakeWikidataClient()
    entity = WikidataEntity(
        name="Jane Doe",
        entity_type="mp",
        qid="Q12345",
        wikidata_url="https://www.wikidata.org/entity/Q12345",
    )

    unresolved = WikidataEntity(name="Unknown Court", entity_type="court")

    enriched = enrich_entities([entity, unresolved], client=client)

    assert enriched[0].attributes["inception_date"] == "1854-05-24"
    assert enriched[0].attributes["party_membership"] == ["Example Party"]
    assert enriched[1] == unresolved
    assert client.property_calls == ["Q12345"]


def test_jsonld_export_is_schema_org_compatible() -> None:
    """Knowledge graph exporter emits parseable schema.org JSON-LD."""
    output = _case_dir("jsonld") / "kg.jsonld"
    entity = WikidataEntity(
        name="Example Party",
        entity_type="party",
        qid="Q7278",
        label="Example Party",
        description="party result",
        wikidata_url="https://www.wikidata.org/entity/Q7278",
        attributes={"inception_date": "1916-07-07"},
    )

    result = export_knowledge_graph_jsonld([entity], output, base_uri="https://example.org/kg/")

    payload = json.loads(result.read_text(encoding="utf-8"))
    assert payload["@context"]["schema"] == "https://schema.org/"
    assert payload["@graph"][0]["@type"] == "schema:Organization"
    assert payload["@graph"][0]["schema:sameAs"] == "https://www.wikidata.org/entity/Q7278"


def test_federated_sparql_example_joins_local_and_wikidata() -> None:
    """Federated query example documents Wikidata SERVICE usage."""
    query = federated_sparql_query_example()
    example_file = Path("data/ontologies/wikidata_federated_example.rq")

    assert "SERVICE <https://query.wikidata.org/sparql>" in query
    assert "schema:sameAs" in query
    assert "wdt:P31" in query
    assert example_file.read_text(encoding="utf-8") == f"{query}\n"


def test_cli_knowledge_graph_exports_jsonld() -> None:
    """CLI writes a JSON-LD knowledge graph from resolved entities."""
    case_dir = _case_dir("cli")
    entities_path = case_dir / "entities.json"
    output = case_dir / "kg.jsonld"
    entities_path.write_text(
        json.dumps(
            [
                {
                    "name": "Jane Doe",
                    "entity_type": "mp",
                    "qid": "Q12345",
                    "wikidata_url": "https://www.wikidata.org/entity/Q12345",
                }
            ]
        ),
        encoding="utf-8",
    )

    rc = main([
        "knowledge-graph",
        "--entities",
        str(entities_path),
        "--output",
        str(output),
        "--base-uri",
        "https://example.org/kg/",
    ])

    assert rc == 0
    parsed = Graph()
    parsed.parse(output, format="json-ld")
    assert len(parsed) > 0


def test_load_wikidata_entities_rejects_non_list_json() -> None:
    """Entity loader rejects non-list JSON documents."""
    entities_path = _case_dir("invalid") / "entities.json"
    entities_path.write_text(json.dumps({"name": "not a list"}), encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a JSON list"):
        load_wikidata_entities(entities_path)
