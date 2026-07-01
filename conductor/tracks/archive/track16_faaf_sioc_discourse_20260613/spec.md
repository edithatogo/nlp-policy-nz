# Track 16: FOAF & SIOC Ontologies for Parliamentary Discourse

**Dependencies**: Track 7 (Downstream API), Track 12 (Entity Linking)
**Parallelization Node**: Semantic Web & Discourse
**Status**: Complete

---

## Goal

Model parliamentary discourse using FOAF for MP/party profiles and SIOC for debate threading. Enable RDF/SPARQL querying of Hansard debates as linked data, consumable by external semantic web tools.

## Scope

### Key Deliverables

1. **FOAF Profile Generator**: RDF profiles for MPs (name, party, role, electorate) from KB data.
2. **SIOC Debate Exporter**: Model Hansard as SIOC containers — speeches as posts, debates as forums, parliament as site.
3. **RDF Serialization**: Turtle/RDF/XML export alongside Parquet as `.ttl` sidecar files.
4. **SPARQL Query CLI**: Basic query interface for RDF graph exploration.

## Ontologies & Standards

- **FOAF**: Person, Organization, Group
- **SIOC**: Post, Forum, Site, Thread
- **RDF/OWL**: W3C linked data standards
- **SKOS**: Party and topic taxonomies

## Acceptance Criteria

- [x] FOAF profile graph generator supports MP identity, party, role, electorate, and Wikidata links from supplied knowledge-base records.
- [x] SIOC containers correctly model Hansard site, debate forum, thread, post, creator, content, and date structure for supplied records.
- [x] RDF export writes valid Turtle sidecars that parse back with `rdflib`.
- [x] CLI `export-rdf` and `sparql` interfaces are functional.
- [x] Focused linked-data package coverage exceeded 90% during implementation.

## Residual external data gate

Track 16 is complete for repo-side linked-data generation, export, and query
contracts. It does not claim that a complete current and historical NZ MP
knowledge base has been harvested or validated. Full-person coverage depends on
the upstream entity/Wikidata corpus maintained by Track 12 and later ontology
coverage work.
