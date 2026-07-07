"""Knowledge-base integration helpers."""

from __future__ import annotations

__all__ = [
    "WIKIDATA_ONTOLOGY_PATH",
    "EntityContext",
    "EntityRecord",
    "EntityResolver",
    "EntityType",
    "JsonSparqlCache",
    "NzEntityResolverComponent",
    "ResolutionBenchmarkCase",
    "ResolvedEntity",
    "WikidataEnricher",
    "WikidataEntity",
    "WikidataResolver",
    "WikidataSparqlClient",
    "default_nz_entities",
    "enrich_entities",
    "evaluate_resolution_precision",
    "export_knowledge_graph_jsonld",
    "federated_sparql_query_example",
    "load_nz_entities",
    "load_ontology_graph",
    "load_wikidata_entities",
    "resolve_entities_in_text",
    "seed_nz_entities",
]


def __getattr__(name: str) -> object:
    """Lazily resolve KB helpers to avoid loading spaCy on import."""
    if name in {
        "EntityContext",
        "EntityRecord",
        "EntityType",
        "default_nz_entities",
        "load_nz_entities",
        "seed_nz_entities",
    }:
        module = __import__("nlp_policy_nz.kb.nz_entities", fromlist=[name])
        return getattr(module, name)
    if name in {
        "EntityResolver",
        "NzEntityResolverComponent",
        "ResolutionBenchmarkCase",
        "ResolvedEntity",
        "evaluate_resolution_precision",
        "resolve_entities_in_text",
    }:
        module = __import__("nlp_policy_nz.kb.resolver", fromlist=[name])
        return getattr(module, name)
    if name == "JsonSparqlCache":
        module = __import__("nlp_policy_nz.kb.sparql_cache", fromlist=[name])
        return getattr(module, name)
    if name == "WikidataEnricher":
        module = __import__("nlp_policy_nz.kb.wikidata", fromlist=[name])
        return getattr(module, name)
    if name in {
        "WIKIDATA_ONTOLOGY_PATH",
        "WikidataEntity",
        "WikidataResolver",
        "WikidataSparqlClient",
        "enrich_entities",
        "export_knowledge_graph_jsonld",
        "federated_sparql_query_example",
        "load_ontology_graph",
        "load_wikidata_entities",
    }:
        module = __import__("nlp_policy_nz.kb.wikidata_kg", fromlist=[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
