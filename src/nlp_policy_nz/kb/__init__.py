"""Knowledge-base integration helpers."""

from nlp_policy_nz.kb.nz_entities import (
    EntityContext,
    EntityRecord,
    EntityType,
    default_nz_entities,
    load_nz_entities,
    seed_nz_entities,
)
from nlp_policy_nz.kb.resolver import (
    EntityResolver,
    NzEntityResolverComponent,
    ResolutionBenchmarkCase,
    ResolvedEntity,
    evaluate_resolution_precision,
    resolve_entities_in_text,
)
from nlp_policy_nz.kb.sparql_cache import JsonSparqlCache
from nlp_policy_nz.kb.wikidata import WikidataEnricher
from nlp_policy_nz.kb.wikidata_kg import (
    WIKIDATA_ONTOLOGY_PATH,
    WikidataEntity,
    WikidataResolver,
    WikidataSparqlClient,
    enrich_entities,
    export_knowledge_graph_jsonld,
    federated_sparql_query_example,
    load_ontology_graph,
    load_wikidata_entities,
)

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
