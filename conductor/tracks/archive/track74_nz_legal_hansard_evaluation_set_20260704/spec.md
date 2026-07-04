# Track 74: NZ Legal/Hansard Held-Out Evaluation Set

## Overview

Create a held-out evaluation set for NZ legislation and Hansard that can be used to select, compare, and gate legal NLP models without contaminating future training runs.

## Requirements

- Define explicit source selection rules for legislation and Hansard material.
- Reserve a held-out split with leakage controls that prevent overlap with training corpora, prior benchmarks, and model-selection fixtures.
- Record provenance for every example, including source, source hash, document version, date, and split reason.
- Define a small but representative evaluation suite that can support model comparison for classification, retrieval, extraction, or stance-style tasks used elsewhere in the repo.
- Keep the dataset deterministic and reproducible from local inputs or CI-fetched fixtures.
- Produce a manifest and validation checks that fail loudly on accidental overlap or schema drift.

## Acceptance Criteria

- [ ] A held-out NZ legal/Hansard split exists with documented selection rules.
- [ ] Leakage checks prove the held-out set does not overlap the defined training pool.
- [ ] A dataset manifest records provenance, hashes, and split metadata for every example.
- [ ] A reproducible evaluation harness loads the set and reports stable baseline metrics.
- [ ] The evaluation set is suitable for gating a later fine-tuning track.

## Out of Scope

- Fine-tuning a model.
- Production deployment or serving changes.
- Benchmarking Mojo or other runtime accelerators.
- Rewriting the corpus ingestion pipeline beyond what is needed to generate the held-out split.
