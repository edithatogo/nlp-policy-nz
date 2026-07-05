# Track 72: Mojo Hotspot Benchmark

**Status**: archived
**Dependencies**: Tracks 19, 42, 56, 67, 70
**Parallelization Node**: Mojo Benchmark Governance

## Phase 1: Baseline Evidence

- [x] Task: Select stable benchmark corpus slices and expected output artifacts.
- [x] Task: Run current benchmark/profiling commands for candidate hot paths.
- [x] Task: Record wall time, memory, input hashes, output hashes, OS, Python version, and lockfile hash.
- [x] Task: Confirm benchmark fixtures are deterministic enough for CI comparison.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Baseline Evidence' (Protocol in workflow.md)

## Phase 2: Candidate Comparison

- [x] Task: Benchmark a Mojo candidate only if Track 70 and Track 71 readiness evidence allows it.
- [x] Task: Compare Mojo against current Python/Rust-backed behavior.
- [x] Task: Compare Mojo against at least one non-Mojo acceleration path such as Rust/PyO3, Polars, LanceDB-native paths, or simpler Python-library improvements.
- [x] Task: Validate artifact parity for offsets, labels, ordering, schema shape, source hashes, and output hashes.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Candidate Comparison' (Protocol in workflow.md)

## Phase 3: Decision Record

- [x] Task: Score the candidate against the Mojo roadmap adoption rubric.
- [x] Task: Record whether Track 73 should proceed, be deferred, or be cancelled.
- [x] Task: Populate and verify the GitHub issue and project fields for Track 72.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Decision Record' (Protocol in workflow.md)

## Implementation Notes

- The live GitHub issue `#79` is closed and records the defer decision for Track 73.
- Archive commit: pending in the next commit.
