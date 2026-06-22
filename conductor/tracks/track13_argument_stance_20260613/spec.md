# Track 13: Argument Mining & Policy Stance Detection

**Dependencies**: Track 5 (Semantic Layer), Track 7 (Downstream API)
**Parallelization Node**: Discourse Analysis
**Status**: In Progress

---

## Goal

Identify argumentative structures in Hansard debates — premises, conclusions, supporting/attacking relations — and classify speakers' stance (pro/con/neutral) on policy issues. Enables downstream corpus-nz-hansard to track policy positions over time.

## Scope

### What This Track Covers

1. **Argument Component Detector**: Identify premise and conclusion spans in debate text using sequential sentence classification with a fine-tuned transformer model.
2. **Relational Argument Graph**: NetworkX-based directed graph mapping premise → conclusion support/attack relations.
3. **Stance Classifier**: Fine-tuned classifier determining pro/con/neutral stance on debated policy issues.
4. **Issue-Argument Linking**: Associate arguments with specific policy topics (Track 5 semantic clusters).
5. **PipelineRecord Enrichment**: Add `arguments: list[dict]` and `stance: str | None` to output schema.

### What This Track Does NOT Cover

- Deontic modality (Track 10)
- Temporal reasoning (Track 11)

## Ontologies & Standards

- **AIF (Argument Interchange Format)**: Core argument structure ontology
- **ACL Anthology Argument Mining**: State-of-the-art component/relation detection

## Acceptance Criteria

- [ ] Argument component classifier achieves >80% F1 on Hansard test set
- [ ] Stance classifier achieves >85% accuracy on held-out debate data
- [x] Argument graphs exportable as AIF-compatible JSON-LD
- [x] PipelineRecord includes `arguments` and `stance` fields
- [x] Test coverage > 90% for repo-side Track 13 surfaces

The remaining unchecked criteria require external held-out evaluation evidence:
500+ human/gold Hansard segments per task, fine-tuned transformer model IDs,
and recorded F1/accuracy reports. Deterministic fixture scores validate wiring
only and must not be used to satisfy those gates.
