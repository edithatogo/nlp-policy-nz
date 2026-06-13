# Track 14: Akoma-Ntoso v3 Schema Compliance & Enrichment

**Dependencies**: Track 4 (Ingestion Engine)
**Parallelization Node**: Schema Standards Compliance
**Status**: Pending

---

## Goal

Upgrade the existing Akoma-Ntoso emitter to full OASIS v3 schema compliance. Extend to all AKN document types (amendment, judgment, debate, bill), implement FRBR hierarchy (Work/Expression/Manifestation/Item), and add comprehensive metadata blocks.

## Scope

### Key Deliverables

1. **Full AKN v3 Compliance**: Validate output against OASIS Akoma-Ntoso XML schema for all NZ document types.
2. **FRBR Hierarchy**: FRBRWork, FRBRExpression, FRBRManifestation, FRBRItem for legislation and debates.
3. **Document Type Emitters**: Amendment, judgment, bill, and debate document types.
4. **Metadata Blocks**: TLCEvent, analysis, and references metadata sections.
5. **Schema Validator**: Automated validation against official OASIS XSD.

## Ontologies & Standards

- **OASIS Akoma-Ntoso v3.0**: Full XML schema
- **CEN MetaLex**: XML interchange standard

## Acceptance Criteria

- [ ] All AKN v3 document types emit valid XML against OASIS XSD
- [ ] FRBR hierarchy correctly populated
- [ ] TLCEvent and analysis metadata blocks included
- [ ] Schema validator runs in CI
- [ ] Test coverage > 90%
