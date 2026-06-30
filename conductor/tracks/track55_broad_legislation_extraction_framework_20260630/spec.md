# Track 55: Broad Legislation Extraction Framework

**Dependencies**: Tracks 4, 10, 11, 14, 15, 18, 26, 27, 54
**Parallelization Node**: Source-Grounded Legislative Extraction
**Status**: In Progress

## Goal

Create a broad extraction framework that treats rules-as-code as one output
family among many source-grounded legislative extractions. `nlp-policy-nz`
remains the producer of extraction records, source traces, manifests, and
publication artifacts that downstream projects consume.

## Extraction Families

The first-class output families are:

- definitions;
- obligations, prohibitions, permissions, and powers;
- conditions, exceptions, eligibility rules, thresholds, and dates;
- entities, cross-references, penalties, delegations, and review rights;
- amendments, commencement, and repeal;
- rules-as-code bridge candidates.

## Accepted Axiom Strengths

- Durable source identity and checksum pins for every extracted record.
- Source-to-output trace manifests for audit and stale-output checks.
- Known-gap ratchets for corpus coverage, parser gaps, and extraction debt.
- Downstream-compatible RuleSpec IDs without depending on a RuleSpec runtime.
- Optional non-executable package skeletons for downstream formula work.

## Library Direction

- Adopt Pydantic 2 for public extraction/export schemas.
- Use `orjson` for deterministic fast JSON rendering where appropriate.
- Add `PyYAML` for future extractor manifest and RuleSpec handoff files.
- Add `pypdf` for optional official-PDF ingestion when no better source exists.
- Add `sqlite-utils` as a candidate local extraction catalog layer.

## Out of Scope

- Executable RuleSpec runtime integration.
- Formula correctness claims for OpenFisca or PolicyEngine outputs.
- Replacing current `PipelineRecord` storage.
- Rust rewrites of core extraction logic; those belong in Track 56.

## Acceptance Criteria

- [x] Pydantic 2 schemas define broad extraction records, source spans, source
  traces, manifests, and run summaries.
- [x] Extraction families include rules-as-code plus non-RaC legislative data.
- [x] Manifest rendering is deterministic and source-checksum grounded.
- [x] CLI or API can emit extraction manifests from pipeline records.
- [x] Extraction manifest schemas are documented for downstream consumers.
- [x] Known-gap and source-span trace reports are generated from local fixtures.
- [x] Optional catalog storage can record extraction run manifests.
