# Specification: source fidelity for cognitive-autopsy consumers

## Problem and scope

The existing HDC profile separates captured evidence, neutral extraction, official findings and downstream interpretation. The implementation programme in `rcagent` additionally needs exact source recovery, attributed accounts and explicit time statements before it can evaluate decision-time reasoning. Generic source hashes and spans in normalised text do not by themselves satisfy those requirements.

This track owns the reusable extraction/export boundary only. It does not implement an RCA reasoner, semantic truth oracle, decision-quality score, process-conformance judgment or medical training pipeline. Existing HDC research ethics is owner-confirmed. New optional benchmark datasets retain their own terms without blocking synthetic contract work or already authorised HDC processing.

## Ownership and integration

| Owner | Responsibility |
| --- | --- |
| `archive-govt-nz` | Authoritative public-source capture, fixity, source-version relationships and replay receipts |
| `nlp-policy-nz` | Neutral extraction, text renditions, source-span mappings, uncertainty and reusable record export |
| `corpus-cases-medilegal-nz` on GitHub | Source/distribution contracts, snapshot/release metadata and source-to-research lineage; no second capture/extraction engine |
| Existing Hugging Face dataset | Canonical public normalised dataset identity, subject to its publication contract |
| `learningfromharm` | Research labels, reference provenance, grouped splits, analyses and manuscripts |
| `rcagent` | Decision-time evidence views, cognitive/RCA interpretation, verification composition and task/model qualification |

Consumer specifications: [component studies](https://github.com/edithatogo/rcagent/blob/8ad5d12ce30837f33027fa3f409bdbe2821fadaa/conductor/research/cognitive-autopsy/component-studies.md), [integration contract](https://github.com/edithatogo/rcagent/blob/8ad5d12ce30837f33027fa3f409bdbe2821fadaa/conductor/research/cognitive-autopsy/integration-contract.md) and [source contract](https://github.com/edithatogo/corpus-cases-medilegal-nz/blob/7c133daf192b5e75adb5733876d72f234c6f0964/docs/cognitive-autopsy-source-contract.md). These immutable references identify reviewed planning revisions and survive branch deletion. Pin mutually compatible release revisions during implementation; these references do not assert release qualification.

## Existing reuse candidates

- [SourceTrace and ExtractedSpan](../../../src/nlp_policy_nz/extraction/schemas.py) provide source hashes and normalised-text ranges. Audit rather than assume raw-text round-trip support.
- [Chunking](../../../src/nlp_policy_nz/syntactic/chunking.py) and [its offset fixtures](../../../tests/test_chunking.py) provide an existing coordinate entry point.
- [Parliamentary source spans](../../../src/nlp_policy_nz/parliament/structure.py) demonstrate attributed, evidence-bearing structure without making their domain labels a clinical schema.
- Existing spaCy, Polars/Arrow, Pydantic/JSON Schema and provenance facilities are the default implementation path. Preserve legal/parliamentary interfaces and default installation behaviour.

## Required contract

1. **Immutable evidence.** Retain the capture receipt and captured bytes, immutable extraction text and their distinct hashes. Store extractor/tool revisions. Do not treat cleaned model features as authoritative text.
2. **Coordinates and mapping.** Specify text encoding, Unicode normalisation, half-open coordinate convention and page/block locators. Retain transformation logs and range mappings back to immutable source text; mark one-to-many, many-to-one, unmappable and lossy spans. Exact quote validation checks the correct rendition, not only span order or length.
3. **Critical fidelity.** Preserve numbers, units, negation, ranges, punctuation, tables, quotations and Māori orthography. Source defects or OCR uncertainty remain represented, not repaired into certainty.
4. **Neutral attribution.** Export source-supported subject/provider/quotation links and evidence-type candidates, with method/revision and uncertainty. Keep official findings attributed to the authority. Conflicting accounts remain separate; source support does not settle truth.
5. **Three clocks.** Represent event/documentation times and explicitly stated delivery/receipt times separately. Allow intervals, unknowns, timezone/granularity limits and competing statements. Receipt/availability is recipient-specific; it does not establish reading, comprehension or knowledge. Do not infer event order from prose order.
6. **Lineage.** Preserve source/case-family/version identifiers supplied by the corpus contract and deterministic extraction run identifiers. Research splits, reviewer labels and altered variants are downstream, not canonical source fields or automatic truth labels.
7. **Scoped export.** A consumer-supplied evidence view includes an opaque ID/hash and allowed source spans. Validate all returned spans against that view, bind caches to its revision, and fail closed on excluded spans or incompatible coordinates. This library does not decide which clinical cutoff or recipient is appropriate.
8. **Private execution.** Reuse local source data only in admitted paths; prevent model downloads, query forwarding, remote telemetry and cloud fallback on restricted runs. Do not put case text into errors or diagnostic logs. Public metadata and model acquisition are separate from sensitive execution.

The implementation should add versioned optional sidecars or profile fields under explicit compatibility tests. Existing source records are not silently rewritten, and the existing HDC YAML design profile is not promoted merely by this plan.

## Dependency and replacement policy

Use the maintained spaCy context/matching, Polars/Arrow and validation facilities already declared. Evaluate medspaCy ConText/section utilities through an optional adapter if they meet a specific unmet extraction requirement. Record package/model revision, licence, runtime, configuration and local-only behaviour. Do not add a required medical dependency, train a model or change lockfiles in this planning update.

Keep the simplest qualified extractor. Remove custom generic code only after a parity fixture set demonstrates preserved output and source mapping. Domain-specific evidence boundaries remain explicit. If an adapter fails, expose the unsupported capability or use the qualified rules path; do not route to a cloud service.

## Acceptance and claim limits

- Exact source-span recovery and named failures are demonstrated on synthetic/authorised fixtures, including Unicode, quotations, units, negation, malformed inputs and extraction-version mismatches.
- Times remain distinct and unknown where unsupported. Conflicting accounts and absent rationale are retained without fabricated reconciliation.
- Scoped export rejects a valid source span outside the permitted view, including from a stale cache or another report version.
- Schema/Polars round-trip and existing legal/parliamentary regression checks pass for the affected contract. Missing evidence is observable rather than silently dropped.
- Consumer fixtures exercise `rcagent` and corpus/research interchange with the same source digests and version/family lineage.
- Results report extraction accuracy, critical errors, useful coverage and unsupported fields for a pinned configuration. A contract-valid fixture is not evidence of clinical validity, general HDC accuracy, cultural authority or permission to publish.

Research-controlled case modifications, LLM comparison scores, fine-tuning decisions, cognitive hypotheses and process interpretation remain in the consuming programme. Source collection and release actions are outside this track's planning completion.
