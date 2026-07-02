# Track 60: LanceDB Retrieval Runtime Hardening

## Overview

Track 60 hardens LanceDB as the repository's local-first vector retrieval
runtime. It records the supported retrieval lifecycle, makes reopen and
corruption handling explicit, and defines when an alternate vector backend
would need to beat LanceDB before it can be considered for substitution.

## Requirements

- Keep LanceDB as the default local/serverless vector store for the CLI, API,
  pipeline search, and RAG wrapper.
- Preserve optional boundaries for Qdrant, FAISS, and DuckDB VSS.
- Cover the supported lifecycle: create, add, search, delete, reopen, and
  corruption-safe fallback.
- Record benchmark evidence for build time, query latency, recall proxy, and
  update latency.
- Document an explicit Qdrant comparison threshold instead of leaving backend
  substitution criteria implicit.
- Keep the Python fallback and current API/pipeline contracts stable.

## Acceptance Criteria

- [ ] The LanceDB adapter safely reopens persisted tables and falls back to an
  empty state when a persisted table cannot be opened.
- [ ] Tests cover create, add, search, delete, reopen, and corruption handling
  for the LanceDB lifecycle.
- [ ] Benchmarks cover build time, query latency, recall proxy, and update
  latency.
- [ ] API and pipeline docs describe the supported retrieval lifecycle and the
  explicit comparison threshold for alternate vector backends.
- [ ] GitHub issue `#62` and Projects `#3` and `#4` remain synchronized with the
  local Conductor track.

## Out of Scope

- Replacing LanceDB with Qdrant, FAISS, or DuckDB VSS by default.
- Making remote Qdrant semantics the primary local test path.
- Adding a production dependency on any alternate vector backend.
