# Track 27: Rules-as-Code Semantic Bridge

**Dependencies**: Tracks 25-26  
**Parallelization Node**: Rules-as-Code Bridge  
**Status**: Planned

## Goal

Expose a rules-as-code intermediate representation that links legal source provisions to OpenFisca/PolicyEngine entities, variables, formulas, parameters, periods, and provenance.

## Scope

- ELI/ELI-DL + AKN source anchors: stable legal identifiers, FRBR/work-expression-version metadata, section-level references, commencement and amendment provenance.
- LKIF + LegalRuleML norm semantics: obligations, permissions, prohibitions, powers, exceptions, defeasibility, applicability conditions.
- OWL-Time / TimeML temporal validity: effective dates, commencement, expiry, assessment periods, parameter histories.
- OpenFisca/PolicyEngine native entities, variables, formulas, parameters, periods.
- SKOS/EuroVoc or NZ local taxonomy for policy domains.
- PROV-O traceability from formula or parameter back to legal source.
- schema.org/Legislation and Wikidata public linked-data discoverability.

## Acceptance Criteria

- [ ] Define a stable rules-as-code bridge schema.
- [ ] Export at least one fixture provision into source anchor, norm semantics, temporal validity, taxonomy, provenance, and OpenFisca/PolicyEngine mappings.
- [ ] Record blockers where formulas cannot be generated because required legal facts or datasets are absent.
- [ ] Add tests proving round-trip JSON serialization and source-provenance preservation.
