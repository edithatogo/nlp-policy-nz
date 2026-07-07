# Track 77: Batch Rules-as-Code Candidate Export

## Overview

Promote the existing single-section `rac-export` bridge into a batch pipeline that consumes the Track 76 source inventory and broad extraction framework to produce source-grounded rules-as-code candidates across New Zealand legislation.

## Functional Requirements

- Add a batch RAC export path that accepts source inventory records, pipeline Parquet outputs, or extraction manifests.
- Produce `ExtractionFamily.RULES_AS_CODE` records with RuleSpec-compatible durable IDs, source spans, checksums, legal-effect metadata, temporal validity, and confidence.
- Emit JSON-LD bridge records and extraction manifests for downstream RuleSpec, PolicyEngine, and OpenFisca consumers.
- Include known-gap and review-status fields so unreviewed model or heuristic outputs cannot be mistaken for executable law.
- Provide CLI and Python API entrypoints with deterministic fixture-backed tests.

## Non-Functional Requirements

- Default execution must be deterministic and fixture-backed in CI.
- Candidate export must preserve exact source spans and checksum-pinned source identity.
- The pipeline must not generate executable rules or formula code in this track.

## Acceptance Criteria

- [ ] Batch RAC export can process multiple source records in one run.
- [ ] Outputs contain source-grounded `rules_as_code` extraction records and JSON-LD bridge payloads.
- [ ] Known gaps and review status are included in manifests.
- [ ] Focused tests cover batch success, partial gaps, invalid inputs, and stable output ordering.
- [ ] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Reviewed legal formula authoring.
- PolicyEngine/OpenFisca runtime package execution.
- Live whole-corpus crawling as a required test.
