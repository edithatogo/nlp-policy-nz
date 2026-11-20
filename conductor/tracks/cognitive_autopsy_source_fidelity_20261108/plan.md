# Plan: cognitive-autopsy source fidelity

Status: planned. Only the planning/reconciliation item can complete in this update; implementation leaves remain open.

## Planning and owner reconciliation

- [x] Record the existing source-profile boundary, current repository status, reuse candidates and bounded implementation leaves; validate planning files and links. Evidence: [planning receipt](./planning-evidence.md).

## Bounded coding-agent leaves

| ID | Dependencies | Deliverable | Acceptance evidence |
| --- | --- | --- | --- |
| NLP-CA01 | None | Inventory existing source/capture/profile/Polars interfaces and freeze a versioned optional export proposal | Exact input/output versions, field ownership, compatibility and rollback are recorded; no duplicate source archive |
| NLP-CA02 | NLP-CA01 | Immutable rendition and transformation/offset sidecar using existing span/provenance types | Source recovery for Unicode, tables, nested quotes, negation, numbers/units; mismatches and lossy maps explicit |
| NLP-CA03 | NLP-CA02 | Rules-first neutral account and explicit-time candidate adapter | Subject/provider remain distinct; event/document/receipt clocks, intervals and unknowns survive serialization; no inferred clinician knowledge |
| NLP-CA04 | NLP-CA03 | Optional medspaCy/spaCy reuse experiment | Same fixture/label budget and admissible source; measured critical errors, coverage and runtime; compatible licence/offline result; no adoption if value absent |
| NLP-CA05 | NLP-CA02 | Permitted-evidence-view export and cache binding | Wrong view/hash/version/range, excluded outcome spans and stale cache rejected; logs/errors omit sensitive text |
| NLP-CA06 | NLP-CA03, NLP-CA05 | Versioned Polars/Arrow export and consumer fixtures | Source/revision/family lineage and uncertainty round-trip; same fixtures consumed by corpus metadata and rcagent interfaces |
| NLP-CA07 | NLP-CA06 | Targeted integration qualification and replacement decision | Affected legacy regressions plus local-only negative tests pass; custom code removed only with parity; record unsupported capabilities |

Optional NLP-CA04 does not block NLP-CA05–07. External benchmark access, model fine-tuning and a complete RCA system are not prerequisites for source-fidelity work.

## Execution state

- [ ] NLP-CA01 — interface inventory and export proposal
- [ ] NLP-CA02 — rendition/offset implementation
- [ ] NLP-CA03 — neutral attribution and three-clock candidates
- [ ] NLP-CA04 — optional maintained clinical adapter comparison
- [ ] NLP-CA05 — scoped export, cache and local-only failures
- [ ] NLP-CA06 — Polars/Arrow and cross-repository fixtures
- [ ] NLP-CA07 — integration evidence and bounded custom-code replacement

## Sequencing and stopping rules

Estimate 1–2 coding-agent days for the contract inventory and initial fidelity fixtures, then 2–4 days for bounded adapters, scoped export and interchange once the source interface is pinned. The optional dependency experiment is a separate 1–2-day spike. These are engineering estimates; obtaining a defensible research reference set and qualifying a corpus/model configuration take evidence rather than elapsed coding time.

Start with synthetic fixtures and authorised records. Unknown receipt times or unresolvable mappings remain unknown/unavailable. A package whose performance or compatibility is insufficient is not required. Do not reinterpret a failed quality gate as a successful schema-only result.

Consumer alignment uses the rcagent work packages CAW01–CAW04, CAW08/CAW10 and the source-preserving side of CAW15–CAW16; those IDs describe integration points, not implementation tasks owned here. `learningfromharm` owns CS01–CS03 reference labels and held-out splits. `rcagent` owns decision-time views and the downstream evaluation runner.

## Validation record

See [planning-evidence.md](./planning-evidence.md). For runtime leaves, add focused behaviour/contract tests before implementation, run the applicable repository checks, and record exact revision/configuration, failures and remaining limits. No execution or publication capability is granted by a checked planning item.
