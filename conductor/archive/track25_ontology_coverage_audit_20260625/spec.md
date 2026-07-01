# Track 25: Ontology Coverage Audit for Existing Systems

**Dependencies**: Tracks 10-18, 22  
**Parallelization Node**: Ontology Discovery & Gap Analysis  
**Status**: Completed

## Goal

Identify the complete ontology or ontology set behind each partly implemented repo system, compare those standards with current implementation coverage, and record data blockers where required source data or authoritative vocabulary data is unavailable.

## Scope

- AKN/LegalDocML emitters and FRBR/TLC metadata.
- PROV-O provenance sidecars and archive metadata.
- FOAF/SIOC parliamentary linked-data exporters.
- Wikidata/schema.org local knowledge graph and SPARQL bridge.
- LKIF-inspired legal effect and deontic modality layer.
- TimeML/OWL-Time-inspired temporal extraction.
- LegalRuleML and Catala-DSL prototype emitters.
- Parliamentary voting/amendment analytics and Isaacus/MLEB integration.
- OpenFisca/PolicyEngine-adjacent rules-as-code outputs.

## Acceptance Criteria

- [x] Produce an ontology coverage matrix with upstream standard, local files, coverage status, missing features, and blocker type.
- [x] Separate implementation gaps from data availability blockers.
- [x] For each blocker, record the dataset/source needed to remove it.
- [x] Add a prioritized implementation backlog feeding Tracks 26-31.
