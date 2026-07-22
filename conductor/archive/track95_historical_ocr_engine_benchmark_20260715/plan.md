# Track 95 Plan
## Phase 1: Reproducible inputs and engines
- [x] Task: Define immutable page/gold input, engine artefact, licence, and container pin contracts (repository-side).
- [x] Task: Add no-cost cloud dispatch and resumable cache evidence contracts.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Reproducible inputs and engines' (Protocol in workflow.md)
## Phase 2: Benchmark decision
- [x] Task: Define all declared metrics and deterministic comparison artefacts.
- [x] Task: Record an explicit deferred-promotion boundary when empirical inputs are absent.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Benchmark decision' (Protocol in workflow.md)

## External gates

The repository-side benchmark contract is complete. Rights-cleared historical
pages, hashed gold annotations, immutable engine/model/container/SBOM pins, and
an actual benchmark run remain external gates. Until supplied, the benchmark
must remain `not_run` and no engine may be promoted.
