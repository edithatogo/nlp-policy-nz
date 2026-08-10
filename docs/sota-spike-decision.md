# Track 105 decision record

Track 105 is an optional, offline spike. It must not change the canonical
spaCy, LanceDB, `PipelineRecord`, or local-first runtime path.

## Allowed

- Optional extras named `structured` for constrained decoding and `graphrag` for
  graph-plus-vector experiments.
- Small, checked-in fixtures and deterministic local demonstrations.
- Candidate JSON validated against existing schemas.
- Non-authoritative evaluation reports that explicitly set
  `promotion_allowed=false`.

## Banned

- Heavy SOTA dependencies in the default install or import path.
- Generative cloud defaults on restricted, Māori, or sovereign paths.
- LLM-as-judge, benchmark scores, or retrieval results as FOI promotion or
  legal-certification oracles.
- Claims of frontier quality without held-out evidence and independent
  review.

The spike can inform future engineering decisions, but it cannot authorize
publication, rights clearance, legal conclusions, or adoption claims.
