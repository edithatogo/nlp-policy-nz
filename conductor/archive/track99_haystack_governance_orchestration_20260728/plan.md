# Plan: Track 99 Haystack optional governance orchestration

Parent: [#189](https://github.com/edithatogo/nlp-policy-nz/issues/189)

## Phase 0: Decision record and dependency boundary ([#190](https://github.com/edithatogo/nlp-policy-nz/issues/190))

- [x] Task: Write failing tests or fixture checks that assert Haystack is not imported on the default runtime path. bf5319f
- [x] Task: Author `docs/haystack-governance-decision.md` with allowed/banned uses (Track 58/60 pattern). bf5319f
- [x] Task: Align `conductor/dependency-policy-matrix.md`, `conductor/maturity-checklist.md`, and `conductor/tech-stack.md` with optional-only Haystack governance scope. a818c6f
- [x] Task: Confirm optional extra remains `rag` or explicitly introduce `orchestration` without making it required. bf5319f
- [x] Task: Conductor - User Manual Verification 'Phase 0: Decision record and dependency boundary' (Protocol in workflow.md) — verified via contract tests + decision doc

## Phase 1: spaCy component adapters and PROV-O dual-write ([#191](https://github.com/edithatogo/nlp-policy-nz/issues/191))

- [x] Task: Write failing tests for SpaCyEnricher / Māori Guard Haystack `@component` sockets and output shapes. bf5319f
- [x] Task: Implement thin adapters under optional `src/nlp_policy_nz/orchestration/haystack/` wrapping `create_nlp_pipeline` and guard helpers. bf5319f
- [x] Task: Dual-write component step metadata into `ProvenanceRecorder` / PROV-O sidecars. bf5319f
- [x] Task: Conductor - User Manual Verification 'Phase 1: spaCy component adapters and PROV-O dual-write' (Protocol in workflow.md) — verified via contract tests

## Phase 2: Deterministic legal-structure indexing ([#192](https://github.com/edithatogo/nlp-policy-nz/issues/192))

- [x] Task: Write failing tests for rights-gate fail-closed behaviour and legal-structure splitter preserving clause boundaries. bf5319f
- [x] Task: Implement indexing DAG: ingest adapter → rights gate → legal splitter → enrich → LanceDB/`PipelineRecord` writer (first-party LanceDB wrapper). bf5319f
- [x] Task: Prove offline fixture run with no external network calls. bf5319f
- [x] Task: Conductor - User Manual Verification 'Phase 2: Deterministic legal-structure indexing' (Protocol in workflow.md) — verified via offline indexing tests

## Phase 3: Extractive QA with verifiable spans ([#193](https://github.com/edithatogo/nlp-policy-nz/issues/193))

- [x] Task: Write failing tests asserting extractive answers are substrings of source text and carry offset/structural evidence. bf5319f
- [x] Task: Implement local extractive Reader path over LanceDB retrieval with pinned local model ids. bf5319f
- [x] Task: Ban generative generators on restricted/sovereign paths by construction in the pipeline graph. bf5319f
- [x] Task: Conductor - User Manual Verification 'Phase 3: Extractive QA with verifiable spans' (Protocol in workflow.md) — verified via extractive substring tests

## Phase 4: Local evaluation and sovereign deploy ([#194](https://github.com/edithatogo/nlp-policy-nz/issues/194))

- [x] Task: Write failing tests for ExactMatch + SAS evaluation scorecard emission on fixtures. bf5319f
- [x] Task: Wire local evaluators; document LLM FaithfulnessEvaluator as non-authoritative for promotion/OIA evidence. bf5319f
- [x] Task: Publish onshore/air-gap deployment checklist (pinned digests, local cache, telemetry egress blocked, generation off by default, sovereignty meta tags). bf5319f
- [x] Task: Record track evidence and explicit no-promotion / no-publication boundary. bf5319f
- [x] Task: Conductor - User Manual Verification 'Phase 4: Local evaluation and sovereign deploy' (Protocol in workflow.md) — verified via scorecard tests + sovereign deploy doc

## Phase: Review Fixes

- [x] Task: Apply review suggestions 140cd1a

## Phase 5: Closeout

- [x] Task: Reconcile Conductor status, parent #189, and subissues #190–#194.
- [x] Task: Archive this track only after automatable work is complete and every remaining external gate is explicit.
- [x] Task: Conductor - User Manual Verification 'Phase 5: Closeout' (Protocol in workflow.md) — repo-side complete; external promotion/publication remain gated elsewhere
