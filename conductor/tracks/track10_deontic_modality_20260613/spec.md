# Track 10: Deontic Modality & Legal Effect Classification

**Dependencies**: Track 4 (Syntactic Layer), Track 5 (Semantic Layer)
**Parallelization Node**: Legal Effect Analysis
**Status**: Pending

---

## Goal

Extract and classify deontic modality expressions from NZ legislation — identifying obligations ("must", "shall"), permissions ("may"), prohibitions ("must not", "shall not"), and dispensations ("need not"). This is the core NLP capability required by the downstream `corpus-law-nz` repo for binding obligation detection.

---

## Scope

### What This Track Covers

1. **Deontic Modality Detector**: A spaCy component that matches modal verb patterns and classifies their deontic type (obligation, permission, prohibition, discretion).
2. **Scope Resolution**: Determine the syntactic scope of each modality (which clause/action is obligated/permitted).
3. **Legal Effect Classification**: Classify entire sections/clauses by their legal effect (duty, power, immunity, liability) using LKIF-inspired categories.
4. **PipelineRecord Enrichment**: Add `deontic_modality` and `legal_effect` fields to the PipelineRecord schema.
5. **Parquet Output Extension**: Include modality annotations in the output schema for downstream consumers.

### What This Track Does NOT Cover

- Temporal reasoning about obligations (Track 11)
- Argument mining or stance (Track 13)
- Coreference resolution

## Ontologies & Standards

- **LKIF (Legal Knowledge Interchange Format)** core deontic categories: Obligation, Prohibition, Permission, Right, Power, Liability
- **OASIS LegalRuleML** for rule representation patterns

## Acceptance Criteria

- [ ] `DeonticModalityDetector` spaCy component registers and extracts modality spans with type labels
- [ ] Modality scope correctly identifies the governed clause/action
- [ ] Legal effect classifier labels sections with LKIF categories
- [ ] PipelineRecord includes `deontic_modality: list[dict]` and `legal_effect: str | None`
- [ ] Parquet output contains new modality columns
- [ ] Test coverage > 90% on NZ legislation test corpus
