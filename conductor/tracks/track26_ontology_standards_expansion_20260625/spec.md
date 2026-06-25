# Track 26: Legislative and Parliamentary Ontology Standards Expansion

**Dependencies**: Track 25  
**Parallelization Node**: Standards Implementation  
**Status**: Planned

## Goal

Add structured support for the missing ontology standards needed to make the corpus interoperable with legal linked data, parliamentary linked data, and rules-as-code tooling.

## Scope

- ELI / ELI-DL metadata model and URI templates.
- ECLI identifiers for case law.
- EuroVoc / SKOS policy-domain vocabularies.
- CEN MetaLex, USLM, LexML, and full schema.org/Legislation.
- Full LKIF and LegalRuleML beyond current inspired/prototype usage.
- Popolo, W3C ORG, DCAT/DCAT-AP.
- Formal OpenFisca/PolicyEngine variable, parameter, entity, formula, and period ontology contracts.

## Acceptance Criteria

- [ ] Each standard has a manifest entry with source URL, license, local representation, and implementation status.
- [ ] Each implemented ontology has tests proving parse/load/export round trips.
- [ ] Standards without source data are represented as explicit blockers, not silent omissions.
- [ ] Public APIs expose stable ontology IDs and mappings for downstream tracks.
