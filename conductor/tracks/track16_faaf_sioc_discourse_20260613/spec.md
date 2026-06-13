# Track 16: FOAF & SIOC Ontologies for Parliamentary Discourse

**Dependencies**: Track 7 (Downstream API), Track 12 (Entity Linking)
**Parallelization Node**: Semantic Web & Discourse
**Status**: Pending

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

- [ ] FOAF profiles for all NZ MPs (current + historical)
- [ ] SIOC containers correctly model Hansard structure
- [ ] RDF export valid against FOAF/SIOC schemas
- [ ] CLI SPARQL interface functional
- [ ] Test coverage > 90%
