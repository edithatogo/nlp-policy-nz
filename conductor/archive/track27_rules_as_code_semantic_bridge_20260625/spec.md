# Track 27: Rules-as-Code Semantic Bridge

**Dependencies**: Tracks 25-26  
**Parallelization Node**: Rules-as-Code Bridge  
**Status**: Completed

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

- [x] Define a stable repo-side rules-as-code bridge schema.
- [x] Export at least one fixture provision into source anchor, norm semantics, temporal validity, taxonomy, provenance, RuleSpec verification, and schema.org/Legislation mappings.
- [x] Record blockers where executable formulas cannot be generated because required OpenFisca/PolicyEngine facts or datasets are absent.
- [x] Add tests proving JSON serialization and source-provenance preservation.
- [x] Add offline OpenFisca/PolicyEngine package skeleton generation with explicit placeholders for target entities, variables, parameters, periods, and oracle fixtures.

## External Gates

- Live executable parity with OpenFisca/PolicyEngine remains external until reviewed formulas and oracle fixtures are supplied.
- PolicyEngine or OpenFisca runtime dependencies are intentionally not required by the default package.
