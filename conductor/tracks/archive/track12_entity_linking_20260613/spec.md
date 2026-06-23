# Track 12: Named Entity Resolution & Wikidata Linking

**Dependencies**: Track 5 (Semantic Layer)
**Parallelization Node**: Knowledge Base Integration
**Status**: Archived

---

## Goal

Resolve named entities from legislation and Hansard — MPs, parties, electorates, ministries, courts — to Wikidata QIDs. Enables federated queries and cross-referencing for downstream repos.

## Scope

### Key Deliverables

1. **NZ Entity Knowledge Base**: Curated entries for MPs (current + historical), parties, electorates, ministries, courts with Wikidata QIDs.
2. **Entity Resolution Pipeline**: spaCy component linking NER spans to KB entries via fuzzy matching and context disambiguation.
3. **Wikidata Enrichment**: SPARQL query module for fetching additional entity metadata.
4. **PipelineRecord Enrichment**: Add `resolved_entities: list[dict]` with QIDs and confidence scores.

## Ontologies & Standards

- **Wikidata Ontology**: Q5 (human), Q7278 (party), Q4112 (electorate)
- **FOAF**: Person profiles (linked from Track 16)

## Acceptance Criteria

- [x] KB contains 200+ MPs, all parties, all electorates
- [x] Entity resolver links spans to KB with >85% precision
- [x] Wikidata SPARQL enrichment works with caching
- [x] Parquet output includes `resolved_entities` column
- [x] Test coverage > 90%
