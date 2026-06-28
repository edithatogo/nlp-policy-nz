# Track 53: NZ Legal Model Evaluation and Selection

**Dependencies**: Track 20 (NZ Legal NLP Fine-Tuning Pipeline), Track 22 (Isaacus Integration), Track 13 (Argument Mining & Policy Stance Detection)
**Parallelization Node**: Model Evaluation and Selection
**Status**: New

---

## Goal

Evaluate the best practical model mix for NZ legal NLP tasks after the Track 13
recommendation update. The track compares local encoder baselines, local legal
LLM adjudicators, and retrieval/linking models for use in downstream NZ
legislation and Hansard workflows.

## Scope

### What This Track Covers

1. Compare `isaacus/emubert` and `nlpaueb/legal-bert-base-uncased` as encoder
   baselines for argument and stance classification.
2. Compare `Equall/Saul-7B-Instruct-v1` and `isaacus/open-australian-legal-llm`
   as silver-label adjudication candidates.
3. Compare Kanon-style embedding/reranking options for retrieval and semantic
   linking.
4. Record model-selection evidence, tradeoffs, and NZ fine-tuning follow-up
   recommendations.

### What This Track Does Not Cover

- Gold-label human annotation work
- Full model fine-tuning on NZ corpora
- Track 13 archive/remediation work

## Acceptance Criteria

- A model selection matrix exists with explicit NZ-task roles.
- The recommended local encoder baseline is justified with measured evidence.
- Silver-label adjudication candidates are separated from gold-label claims.
- Retrieval/linking candidates are separated from classifier candidates.
- Follow-up work for NZ-legislation fine-tuning is recorded.

## Out of Scope

- Production deployment
- New pipeline schema fields
- Archived track maintenance
