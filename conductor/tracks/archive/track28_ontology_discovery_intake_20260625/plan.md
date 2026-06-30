# Track 28: Ontology Discovery and Intake

**Dependencies**: Track 25
**Parallelization Node**: Standards Discovery
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Search official standards bodies: OASIS (AKN), W3C (OWL, RDF, PROV, SKOS, DCAT, ORG, Time Ontology), IEC/ISO (MetaLex), EU publications (ELI, ECLI, EuroVoc), UN/CEFACT | [x] | `track28_discovery_log.json` |
| 2 | Search government vocabulary platforms: data.govt.nz, NZ Legislation Advisory Committee, FIGI, AGLS, NZGLS | [x] | `track28_discovery_log.json` |
| 3 | Search legal informatics literature: ICAIL, JURIX, Frontiers in AI + Law for recently published ontologies | [x] | Legal-informatics monitor candidates in discovery log |
| 4 | Search rules-as-code tooling: OpenFisca, PolicyEngine, Catala, Docassemble, ErgoAI, Stoica | [x] | Rules-as-code candidates in discovery log |
| 5 | Record candidate metadata: name, source URL, authority, license, format, NZ relevance score, implementation effort estimate | [x] | `data/ontologies/track28_discovery_log.json` |
| 6 | Score candidates on authority (W3C REC > community draft), NZ applicability, interoperability with existing ontologies, license/access restrictions, maintenance status | [x] | `data/ontologies/track28_triage.json` |
| 7 | Add approved candidates to `data/ontologies/standards_registry.json` (from Track 26) and update blocker register with data-access blockers | [x] | `track28_standards_registry_addendum.json`, `track28_blockers.json` |
| 8 | Write tests validating candidate scoring and registry integrity | [x] | `tests/test_track28_ontology_discovery.py` |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
