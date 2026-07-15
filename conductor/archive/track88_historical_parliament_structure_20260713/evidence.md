# Track 88 Evidence

## Implemented

- `nlp_policy_nz.parliament.structure` provides frozen hierarchy nodes, speaker attributions, semantic links, review items, page/block source spans, deterministic IDs, JSON-LD export, and an adapter contract for optional model-backed extractors.
- Deterministic extraction recognizes volume-adjacent page structure including sessions, sittings, dates, debates, questions, speeches, divisions, tables, and appendices.
- Speaker labels are normalized conservatively; generic labels abstain and enter a review queue rather than receiving an invented identity.
- Link extraction retains evidence for legislation, agencies, places, iwi/hapu, committees, petitions, and cited publications.
- `nlp_policy_nz.parliament.evaluation` measures hierarchy, speaker, link F1, source-span fidelity, and abstention recall with fail-closed promotion thresholds.
- `data/track88/golden_annotations.json` defines metadata-only, temporally and typographically stratified held-out evaluation controls.

## Verification

- Track 88 tests: 9 passed.
- New structure/evaluation module coverage: 92.63%.
- `basedpyright src/nlp_policy_nz/parliament/structure.py src/nlp_policy_nz/parliament/evaluation.py`: 0 errors, 0 warnings, 0 notes.
- Ruff check and format checks passed for all Track 88 source and test files.

## Boundaries

- The extractor does not download corpus content or claim historical completeness.
- Identity resolution is deterministic and uncertainty-aware; external authority reconciliation and corpus-scale cloud execution remain downstream work in Tracks 89-91.
- The gold artifact contains no document text or OCR payload, preventing evaluation leakage.

## Independent audit disposition — 2026-07-15

The three-review panel confirmed that the deterministic prototype, review queue,
source-span model, semantic-link contract, and evaluator are implemented. The
so-called gold artifact is metadata-only, however, so it cannot prove held-out
hierarchy or speaker performance. Authority-backed temporally valid identities
and independently annotated/adjudicated historical text are also absent. No
extractor or identity mapping is promoted. The missing empirical evaluation is
tracked by Track 96 / issue #132.
