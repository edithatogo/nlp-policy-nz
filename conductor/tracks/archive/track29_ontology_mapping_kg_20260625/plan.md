# Track 29: Ontology Mapping Knowledge Graph

**Dependencies**: Tracks 25-28
**Parallelization Node**: Ontology Alignment & Visualization
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Define mapping record schema (JSON Schema): source_standard, target_standard, source_term, target_term, mapping_predicate (skos:exactMatch, skos:closeMatch, rdfs:subClassOf, owl:equivalentClass), confidence, method, provenance | [x] | conductor_orchestrator |
| 2 | Create `src/nlp_policy_nz/ontology/mapping_graph.py` with mapping record CRUD, validation, and query by standard pair | [x] | conductor_orchestrator |
| 3 | Create `data/ontologies/ontology_mappings.json` with seed mappings: LKIF -> AKN, FOAF -> schema.org, SIOC -> AKN, PROV-O -> DCAT | [x] | conductor_orchestrator |
| 4 | Build RDF/JSON-LD graph export: serialize mapping graph as Turtle or JSON-LD for SPARQL querying | [x] | conductor_orchestrator |
| 5 | Add cross-ontology query helpers: `get_equivalent(concept, from_std, to_std)` and `traverse_mappings(concept, from_std, max_hops)` | [x] | conductor_orchestrator |
| 6 | Generate mapping-network summary statistics and visualization (Mermaid graph or NetworkX plot) | [x] | conductor_orchestrator |
| 7 | Write tests: schema validation, round-trip serialization, equivalent concept resolution, graph export integrity | [x] | conductor_orchestrator |
| 8 | Document mapping methodology and known gaps in `docs/ontology_mapping.md` | [x] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
