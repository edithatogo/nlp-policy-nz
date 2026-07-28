# Track 99: Haystack optional governance orchestration layer

Parent issue: [#189](https://github.com/edithatogo/nlp-policy-nz/issues/189)

Subissues:

- [#190](https://github.com/edithatogo/nlp-policy-nz/issues/190) Decision record and dependency boundary
- [#191](https://github.com/edithatogo/nlp-policy-nz/issues/191) spaCy `@component` adapters and PROV-O dual-write
- [#192](https://github.com/edithatogo/nlp-policy-nz/issues/192) Deterministic legal-structure indexing pipeline
- [#193](https://github.com/edithatogo/nlp-policy-nz/issues/193) Extractive QA with verifiable spans
- [#194](https://github.com/edithatogo/nlp-policy-nz/issues/194) Local semantic evaluation and sovereign deploy config

## Overview

Prototype [Haystack](https://github.com/deepset-ai/haystack) as an **optional, deterministic, pipeline-first orchestration shell** for New Zealand AI and data governance accountability. The goal is typed component graphs, replayable indexing recipes, extractive span evidence, local evaluation scorecards, and onshore/air-gapped deployment — not a generative chatbot product.

Canonical engines remain spaCy, msgspec/`PipelineRecord`, LanceDB, and PROV-O sidecars. Haystack may wrap them; it must not replace them.

## Functional requirements

1. **Decision boundary:** Document allowed and banned Haystack uses (same pattern as Track 58 LangGraph and Track 60 LanceDB).
2. **Component adapters:** Wrap existing spaCy / guard / legal enrichment as `@component` classes with typed sockets; preserve linguistic logic.
3. **Indexing DAG:** Local batch pipeline: ingest → rights gate → legal-structure split → enrich → LanceDB/Document write, offline by default.
4. **Extractive audit QA:** Local extractive Reader over retrieval returning verbatim spans with document/section/offset evidence.
5. **Evaluation:** ExactMatch + local SAS with pinned onshore encoders; LLM FaithfulnessEvaluator is non-authoritative for promotion.
6. **Sovereign deploy:** Document fully local/onshore/air-gapped configuration, telemetry egress controls, and sovereignty metadata tags.

## Non-functional requirements

- `haystack-ai` remains an optional extra only (existing `rag` extra or explicitly renamed `orchestration`).
- Default CI and runtime paths must not require Haystack.
- No external API calls on restricted/sovereign default paths.
- Dual-write orchestration steps into existing PROV-O provenance.
- TDD for all new adapter code.

## Acceptance criteria

- Parent #189 and subissues #190–#194 are linked from this track and the registry.
- Decision record states allowed/banned uses and updates dependency/maturity docs.
- At least one optional indexing prototype and one extractive QA prototype run offline on fixtures.
- Evidence notes record limitations; no legal promotion or publication claims from this track alone.

## Out of scope

- Making Haystack a required dependency.
- Replacing LanceDB, spaCy, or `PipelineRecord` as canonical stores/engines.
- Generative cloud LLM defaults on restricted / Māori / sovereign data.
- Using LLM faithfulness scores as OIA or promotion evidence.
- Rights clearance, FOI promotion, or registry publication (other tracks/issues).
