# HDC medico-legal source profile

This design profile defines the active processing boundary for public New Zealand Health and Disability Commissioner decisions.

## Repository responsibilities

- `archive-govt-nz` owns public-source capture, fixity, version relations and replay receipts.
- `nlp-policy-nz` owns neutral extraction, evidence spans, missingness and source-linked record production.
- `corpus-cases-medilegal-nz` on GitHub owns source/distribution contracts, snapshot/release metadata and source-to-research lineage; its active repository status does not create a second capture or extraction pipeline.
- the existing Hugging Face dataset `edithatogo/corpus-cases-medilegal-nz` remains the canonical public normalised dataset identity.
- `learningfromharm` owns research labels, splits and analyses; `rcagent` owns decision-time evidence views, cognitive/RCA interpretation and component qualification. Those outputs remain downstream of the canonical source record.

The August 2026 profile described the GitHub corpus repository as archived. Live repository metadata checked on 2026-11-08 reports `archived: false`, and the owner has requested coordinated research contracts in that repository. This corrects the status description while preserving the capture and extraction boundaries above; it does not authorise a competing pipeline or a dataset release.

## Record separation

The processing pipeline must preserve separate layers for:

1. captured source bytes and capture metadata;
2. extraction evidence and source spans;
3. official findings expressed in the authoritative decision;
4. neutral bibliographic and case metadata;
5. project-derived classifications, which remain downstream and reversible.

An extractor may propose a candidate finding span, recommendation span or review/remedy span. It may not infer a legal conclusion, clinical truth, credentialing failure or cognitive-autopsy score (the legacy YAML key is `decision_autopsy_score`).

## Evidence and uncertainty

Every candidate record should retain the authoritative URL, source content digest, retrieval receipt, record revision and extraction uncertainty. Missing or ambiguous fields remain missing or ambiguous. Extraction output must not silently overwrite a reviewed canonical record.

## Privacy and cultural limits

The profile should use minimum-necessary public metadata and avoid amplifying personal information beyond the authoritative public source without review. Correct Māori orthography and source-carried cultural terms should be preserved. Technical conformance does not constitute Māori, consumer, legal or clinical validation.

## Publication boundary

Publication to the existing Hugging Face dataset requires separate validation of row schema, rights, privacy, versioning and release status. This profile does not itself publish rows.

## Claim boundary

A passing profile and fixtures would establish a reproducible neutral-processing contract. They would not establish corpus completeness, legal interpretation, clinical truth, cultural authority, credentialing conclusions or downstream research validity.

Related design issue: [#313](https://github.com/edithatogo/nlp-policy-nz/issues/313) (closed). Its closure is not evidence that the additional runtime contracts below have been implemented.

## Planned cognitive-autopsy source-fidelity extension

The [owner-local Conductor track](../../conductor/tracks/cognitive_autopsy_source_fidelity_20261108/index.md) implements the source-side requirements of [rcagent #117](https://github.com/edithatogo/rcagent/pull/117), [learningfromharm #8](https://github.com/edithatogo/learningfromharm/pull/8) and [corpus-cases-medilegal-nz #30](https://github.com/edithatogo/corpus-cases-medilegal-nz/pull/30). The existing YAML remains a design profile; this document does not change its runtime schema or activate an adapter.

| Proposed evidence group | Neutral export requirement | Downstream interpretation boundary |
| --- | --- | --- |
| Raw capture and text rendition | Capture digest/receipt, immutable extracted-text digest, extractor revision and explicit coordinate system; keep normalised features separate | A PDF digest alone does not establish the text offsets of a particular extraction |
| Span mapping and text fidelity | Versioned mapping from transformed spans to retained source-text ranges and page/block locators, including many-to-one or lossy transformations | Reject unverifiable exact-quote claims; do not silently substitute cleaned text |
| Attribution and assertion candidates | Subject, account-provider and quoted/section evidence spans; optional assertion/uncertainty labels with method provenance | A faithful account is not an established event; documented rationale absence is not proof of absent reasoning |
| Explicit time statements | Separate event time, document time and delivery/receipt statements; retain recipient references, intervals, timezones/granularity, contradictions and unknowns | Delivery is not reading or knowledge; `rcagent` constructs decision-time information states |
| Version and family lineage | Source record/revision, capture and rendition hashes, linked report/case-family identifiers, transformation lineage | `learningfromharm` owns train/development/test splits and reference annotations; variants cannot become new independent source cases |
| Permitted evidence view | Preserve consumer-supplied packet/view identifiers, hashes and allowed source spans in scoped exports | No widening of the view, retrieval of excluded text, later-outcome injection or cloud fallback |

Fidelity fixtures must cover numbers, units, ranges, negation, punctuation, nested quotation, tables, Māori orthography and Unicode composition. Retain the original text even when a normalised feature representation is useful. Missing or ambiguous material remains explicit.

Reuse spaCy and Polars/provenance contracts first. Compare an optional medspaCy adapter with the existing bounded rules on synthetic or already authorised inputs; a dependency or model is accepted only within the tested extraction task. Source-specific benchmark labels, cognitive hypotheses, controlled case variants and clinical validity judgments stay in downstream research artefacts. No data or weights are published by this extension.
