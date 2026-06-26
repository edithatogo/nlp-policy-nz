# Track 28: Ontology Discovery and Intake

**Dependencies**: Track 25
**Parallelization Node**: Standards Discovery
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Search official standards bodies: OASIS (AKN), W3C (OWL, RDF, PROV, SKOS, DCAT, ORG, Time Ontology), IEC/ISO (MetaLex), EU publications (ELI, ECLI, EuroVoc), UN/CEFACT | [ ] | conductor_orchestrator |
| 2 | Search government vocabulary platforms: data.govt.nz, NZ Legislation Advisory Committee, FIGI, AGLS, NZGLS | [ ] | conductor_orchestrator |
| 3 | Search legal informatics literature: ICAIL, JURIX, Frontiers in AI + Law for recently published ontologies | [ ] | conductor_orchestrator |
| 4 | Search rules-as-code tooling: OpenFisca, PolicyEngine, Catala, Docassemble, ErgoAI, Stoica | [ ] | conductor_orchestrator |
| 5 | Record candidate metadata: name, source URL, authority, license, format, NZ relevance score, implementation effort estimate | [ ] | conductor_orchestrator |
| 6 | Score candidates on authority (W3C REC > community draft), NZ applicability, interoperability with existing ontologies, license/access restrictions, maintenance status | [ ] | conductor_orchestrator |
| 7 | Add approved candidates to `data/ontologies/standards_registry.json` (from Track 26) and update blocker register with data-access blockers | [ ] | conductor_orchestrator |
| 8 | Write tests validating candidate scoring and registry integrity | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
