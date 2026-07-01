# Track 17: Wikidata NZ Ontology Integration

**Dependencies**: Track 12 (Entity Linking)
**Parallelization Node**: Knowledge Graph
**Status**: Complete

---

## Goal

Create a formal OWL mapping from NZ legislative and parliamentary concepts to Wikidata, enabling federated SPARQL queries and cross-repository knowledge graph integration. Link Acts, MPs, parties, electorates to their Wikidata QIDs.

## Scope

### Key Deliverables

1. **Wikidata NZ Ontology Map**: OWL file mapping NZ legal concepts to Wikidata classes and properties.
2. **Bulk QID Resolver**: SPARQL-based batch name-to-QID resolution with caching.
3. **Property Enrichment**: Fetch additional properties (dates, party membership periods) from Wikidata.
4. **Federated SPARQL**: Enable queries joining nlp-policy-nz data with Wikidata.
5. **Knowledge Graph Export**: JSON-LD knowledge graph with Wikidata-annotated entities.

## Ontologies & Standards

- **Wikidata Ontology**: Q-item and P-property mapping
- **OWL 2**: Formal ontology definitions
- **SPARQL 1.1**: Federated query protocol
- **JSON-LD**: Knowledge graph serialization

## Acceptance Criteria

- [x] OWL mapping file covers NZ Acts, MPs, parties, electorates, and courts.
- [x] Bulk QID resolver provides cached exact-name SPARQL resolution with deterministic fake-client tests.
- [x] Property enrichment populates resolved entities with Wikidata attributes.
- [x] Federated SPARQL query examples are documented and checked in.
- [x] JSON-LD export is parseable and schema.org-compatible.
- [x] Focused `kb` package coverage exceeded 90% during implementation.

## Residual external data gate

Track 17 is complete for repo-side ontology mapping, cached resolver, property
enrichment, federated-query example, CLI export, and JSON-LD contracts. It does
not claim measured >90% precision against a live Wikidata gold evaluation set;
that gate requires a curated target entity benchmark and live or snapshotted
Wikidata reconciliation evidence.
