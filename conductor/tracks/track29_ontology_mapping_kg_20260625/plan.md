# Track 29: Ontology Mapping Knowledge Graph

**Dependencies**: Tracks 25-28
**Parallelization Node**: Ontology Alignment & Visualization
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Define mapping record schema (JSON Schema): source_standard, target_standard, source_class/property, target_class/property, mapping_predicate (skos:exactMatch, skos:closeMatch, rdfs:subClassOf, owl:equivalentClass), confidence, method, provenance | [ ] | conductor_orchestrator |
| 2 | Create `src/nlp_policy_nz/ontology/mapping_graph.py` with mapping record CRUD, validation, and query by standard pair | [ ] | conductor_orchestrator |
| 3 | Create `data/ontologies/ontology_mappings.json` with seed mappings: LKIF -> AKN, FOAF -> schema.org, SIOC -> AKN, PROV-O -> DCAT | [ ] | conductor_orchestrator |
| 4 | Build RDF/JSON-LD graph export: serialize mapping graph as Turtle or JSON-LD for SPARQL querying | [ ] | conductor_orchestrator |
| 5 | Add cross-ontology query helpers: `get_equivalent(concept, from_std, to_std)` and `traverse_mappings(concept, max_hops)` | [ ] | conductor_orchestrator |
| 6 | Generate mapping-network summary statistics and visualization (Mermaid graph or NetworkX plot) | [ ] | conductor_orchestrator |
| 7 | Write tests: schema validation, round-trip serialization, equivalent concept resolution, graph export integrity | [ ] | conductor_orchestrator |
| 8 | Document mapping methodology and known gaps in `docs/ontology_mapping.md` | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
