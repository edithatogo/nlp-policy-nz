# Track 60: LanceDB Retrieval Runtime Hardening

**Dependencies**: Tracks 6, 22, 33, 44, 52
**Parallelization Node**: Vector Retrieval and Local Search
**Status**: planned

## Phase 1: LanceDB Hardening

- [~] Task: Register Track 60 in `conductor/tracks.md` and mirror the issue and
  project state for GitHub issue `#62`.
- [ ] Task: Harden `LanceDBAdapter` reopen and corruption handling so a
  persisted table can be reopened safely and a failed reopen falls back to an
  empty index state.
- [ ] Task: Expand LanceDB lifecycle coverage in `tests/test_vectordb.py` for
  create, add, search, delete, reopen, and corruption handling.
- [ ] Task: Extend `tests/benchmarks/test_vector_benchmark.py` to measure build
  time, query latency, recall proxy, and update latency for LanceDB.
- [ ] Task: Update `docs/vector-store-dependency-decision.md` and the search
  entrypoint docs to record the supported retrieval lifecycle and explicit
  backend comparison threshold.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: LanceDB Hardening'
  (Protocol in workflow.md)

## Phase 2: Closeout

- [ ] Task: Verify the local metadata, spec, plan, and index parse correctly.
- [ ] Task: Verify the GitHub issue mirror and project items remain in sync
  after the implementation updates.
- [ ] Task: Mark Track 60 complete in `conductor/tracks.md` and capture the
  implementation evidence.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Closeout' (Protocol
  in workflow.md)
