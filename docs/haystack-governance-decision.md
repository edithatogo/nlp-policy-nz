# Haystack Governance Orchestration Decision

Track 99 evaluates Haystack only as an optional governance orchestration layer for typed, auditable legal NLP workflows. Canonical engines remain spaCy helpers, `LanceDBAdapter`, `PipelineRecord`, and `ProvenanceRecorder`.

Parent issue: [#189](https://github.com/edithatogo/nlp-policy-nz/issues/189)  
Subissues: [#190](https://github.com/edithatogo/nlp-policy-nz/issues/190)–[#194](https://github.com/edithatogo/nlp-policy-nz/issues/194)

## Allowed contexts

- Typed DAG orchestration for auditability.
- Legal indexing shell with structure preservation.
- Extractive span QA with verifiable offsets.
- Local ExactMatch and SAS-proxy evaluation.
- Onshore and air-gap deployments.

## Banned contexts

- Required runtime dependency for default CI or CLI paths.
- Replacement for spaCy helpers, `LanceDBAdapter`, or `PipelineRecord`.
- Generative cloud defaults on restricted or sovereign data.
- LLM FaithfulnessEvaluator as promotion or OIA evidence oracle.

## Optional dependency boundary

`haystack-ai` remains behind the optional extras:

- `rag = ["haystack-ai>=2.0.0"]`
- `orchestration = ["haystack-ai>=2.0.0"]` (alias)

Default Pixi and CI environments must not require Haystack. The pure-Python prototype under `src/nlp_policy_nz/orchestration/haystack/` provides a CI-safe fallback that mirrors Haystack component shapes without importing `haystack-ai`.

## Runtime policy

- No generative LLM defaults; extractive spans only.
- `FAITHFULNESS_EVALUATOR_AUTHORITATIVE = False` — Haystack FaithfulnessEvaluator output is non-authoritative.
- `GENERATIVE_DEFAULT_ALLOWED = False` — generation stays off unless an explicit, audited override is added later.
- Rights gates fail closed for restricted, Māori, and sovereign access classes without `rights_cleared: true`.

## No-promotion / no-publication boundary

Track 99 delivers a prototype orchestration shell and local evaluation scorecards only. It does **not** authorize:

- promotion of model outputs to production or publication tiers,
- use as OIA or compliance evidence without human review,
- bypass of `PipelineRecord` or PROV-O provenance requirements,
- publication of restricted or sovereign-source material.

Evidence from this track is for engineering evaluation and governance review only.
