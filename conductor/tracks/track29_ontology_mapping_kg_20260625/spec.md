# Track 29: Ontology Mapping Knowledge Graph

**Dependencies**: Tracks 25-28  
**Parallelization Node**: Ontology Alignment & Visualization  
**Status**: Planned

## Goal

Represent explicit ontology mappings in a graph so the system can understand, query, and visualize relationships between ontology classes, properties, datasets, and pipeline outputs.

## Scope

- Explicit mappings and crosswalks only; inferred mappings belong in Track 30.
- Stable mapping predicates such as exact, close, broad, narrow, related, equivalent class, equivalent property, and source-derived crosswalk.
- RDF/Turtle, JSON-LD, SPARQL/query helpers, and visual graph artefacts.

## Acceptance Criteria

- [ ] Store explicit mappings with source, confidence, and review status.
- [ ] Export mapping graph as RDF/Turtle and JSON-LD.
- [ ] Provide query helpers for mapping inspection.
- [ ] Produce at least one visual graph artefact for ontology relationships.
