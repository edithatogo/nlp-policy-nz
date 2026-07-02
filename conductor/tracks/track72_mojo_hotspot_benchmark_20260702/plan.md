# Track 72: Mojo Hotspot Benchmark

**Status**: planned
**Dependencies**: Tracks 19, 42, 56, 67, 70
**Parallelization Node**: Mojo Benchmark Governance

## Phase 1: Baseline Evidence

- [ ] Task: Select stable benchmark corpus slices and expected output artifacts.
- [ ] Task: Run current benchmark/profiling commands for candidate hot paths.
- [ ] Task: Record wall time, memory, input hashes, output hashes, OS, Python version, and lockfile hash.
- [ ] Task: Confirm benchmark fixtures are deterministic enough for CI comparison.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Baseline Evidence' (Protocol in workflow.md)

## Phase 2: Candidate Comparison

- [ ] Task: Benchmark a Mojo candidate only if Track 70 and Track 71 readiness evidence allows it.
- [ ] Task: Compare Mojo against current Python/Rust-backed behavior.
- [ ] Task: Compare Mojo against at least one non-Mojo acceleration path such as Rust/PyO3, Polars, LanceDB-native paths, or simpler Python-library improvements.
- [ ] Task: Validate artifact parity for offsets, labels, ordering, schema shape, source hashes, and output hashes.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Candidate Comparison' (Protocol in workflow.md)

## Phase 3: Decision Record

- [ ] Task: Score the candidate against the Mojo roadmap adoption rubric.
- [ ] Task: Record whether Track 73 should proceed, be deferred, or be cancelled.
- [ ] Task: Populate and verify the GitHub issue and project fields for Track 72.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Decision Record' (Protocol in workflow.md)
