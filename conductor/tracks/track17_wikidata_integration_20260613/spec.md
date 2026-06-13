# Track 17: Wikidata NZ Ontology Integration

**Dependencies**: Track 12 (Entity Linking)
**Parallelization Node**: Knowledge Graph
**Status**: Pending

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

- [ ] OWL mapping file covers NZ Acts, MPs, parties, electorates, courts
- [ ] Bulk QID resolver achieves >90% precision
- [ ] Property enrichment populates KB with Wikidata attributes
- [ ] Federated SPARQL query examples documented
- [ ] JSON-LD export valid against schema.org
- [ ] Test coverage > 90%
