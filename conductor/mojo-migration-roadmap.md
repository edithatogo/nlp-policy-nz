# Mojo Migration Roadmap

## Purpose

This roadmap records a staged path for introducing Mojo into `nlp-policy-nz` where it can materially improve GitHub Actions and batch-pipeline performance without destabilizing the current Python, Rust-backed Python, Pixi, and Windows development workflows.

The goal is not a wholesale rewrite. The goal is to identify hot, deterministic, low-dependency kernels that can run faster in Linux CI while keeping the public Python API, Parquet artifacts, conductor tracks, and downstream repository contracts stable.

## Current position

`nlp-policy-nz` is a Python-first research and production pipeline with performance-sensitive pieces already delegated to Rust-backed libraries:

- `msgspec` and `orjson` for schema and JSON performance.
- Polars, Arrow, and Parquet for tabular data flow.
- LanceDB for local vector storage.
- Hugging Face fast tokenizers and spaCy/Thinc for NLP runtime behavior.
- Optional Rust/PyO3/maturin work remains available for extension modules.

Mojo is a future candidate for focused compute kernels, but it must earn adoption through benchmarks, packaging evidence, CI support, and compatibility with this repo's fallback-first Windows development workflow.

## External state to track

As of July 2, 2026:

- The PyPI `mojo` package is published by Modular Inc and includes the compiler, standard library, LSP, debugger, and related tooling.
- PyPI metadata says Mojo is not available for Windows.
- Current wheels are for Linux and macOS targets, which means this repo cannot make Mojo required for the default Windows workstation workflow yet.
- Modular's public platform repository includes MAX and Mojo components, with Mojo examples, standard-library material, and MAX kernels.
- Because most production-style execution for this repo is expected to happen in GitHub Actions, Linux CI can be the first real Mojo target while Windows keeps exercising Python fallback behavior.

Source references:

- `https://pypi.org/project/mojo/`
- `https://pypi.org/project/mojo-compiler/`
- `https://github.com/modular/modular`
- `https://mojolang.org/docs/manual/`

## Migration principles

1. Keep Python as the stable public API.
2. Keep all existing Python tests as the behavioral oracle.
3. Only migrate code after profiling proves a material bottleneck.
4. Prefer replacing private kernels, not public data models.
5. Keep Mojo optional until Windows support, GitHub Actions support, and packaging are reliable enough for the target profile.
6. Maintain byte-for-byte or schema-level parity for generated JSON, CSV, Parquet, RDF, and Markdown artifacts.
7. Do not introduce Mojo into legal reasoning, ontology, or publication paths where correctness explainability is more important than throughput.
8. Treat Mojo, Rust, Polars plugins, msgspec, and vector-store improvements as competing acceleration options, not automatic complements.
9. Optimize first for Linux GitHub Actions where that is the practical high-frequency runtime, but never let that remove the Windows/Python fallback path.

## Highest-impact staged adoption path

### Stage 0: Bring Mojo planning under conductor control

Objective: keep the migration measurable and reversible.

Tasks:

- Keep this roadmap linked from the tech stack and improvement backlog.
- Create a future conductor track for Mojo readiness and hotspot benchmarking before any runtime code changes.
- Confirm the current GitHub Actions runner profile, expected cache behavior, and artifact retention needs.
- Confirm whether Mojo should be installed through `mojo`, `mojo-compiler`, Pixi, or a dedicated setup action.

Exit criteria:

- The planned Mojo profile is Linux-only, optional, and non-blocking.
- Windows and default CI behavior are explicitly documented as Python fallback.
- The next track has measurable benchmark acceptance criteria.

### Stage 1: Profile before porting

Objective: identify the highest-impact kernels in the repo rather than guessing.

Tasks:

- Run current benchmark and profiling commands against representative fixtures:
  - `pixi run benchmark`
  - `pixi run profile`
  - targeted `pytest-benchmark` runs under `tests/benchmarks`
- Capture wall time, memory, input hashes, output hashes, Python version, OS, and dependency lockfile hash.
- Compare candidate hotspots against existing Rust-backed options before writing Mojo.

Likely first candidates, in priority order:

1. Citation and provision span matching.
2. Extraction manifest projection.
3. Hot text normalization loops.
4. LanceDB vector post-processing.
5. Batch scoring and review aggregation.

Exit criteria:

- At least one candidate has reproducible bottleneck evidence.
- The benchmark fixture is stable enough for CI.
- A non-Mojo alternative is documented for comparison.

### Stage 2: Add Linux-only Mojo experiment sandbox

Objective: prove the toolchain and parity model without touching production imports.

Tasks:

- Add `experiments/mojo/` only after Linux install is verified.
- Add a tiny deterministic kernel plus Python reference output.
- Add a non-blocking Linux GitHub Actions job or matrix entry.
- Keep Windows CI and default test jobs free of Mojo requirements.
- Generate benchmark artifacts under `artifacts/mojo/` or CI artifacts.

Exit criteria:

- Linux GitHub Actions can install Mojo and run the sandbox.
- Windows jobs skip Mojo cleanly.
- Python and Mojo outputs match for the sandbox fixture.
- CI failures in the Mojo experiment do not block ordinary validation until production gates are met.

### Stage 3: Prototype the highest-impact kernel

Objective: test Mojo on a real repo bottleneck.

Preferred first kernel:

- Citation/provision span matching if profiling shows repeated pattern scans dominate.
- Extraction manifest projection if serialization/projection dominates.

Tasks:

- Implement a Mojo prototype behind `experiments/mojo/`.
- Keep the Python implementation canonical.
- Add parity checks for offsets, labels, ordering, schema shape, source hashes, and output hashes.
- Benchmark end-to-end pipeline impact, not just kernel runtime.

Exit criteria:

- Mojo beats the Python/Rust-backed baseline by the agreed threshold.
- Mojo also compares favorably against Rust/PyO3, Polars-native, or simpler Python-library improvements.
- Artifact parity passes.

### Stage 4: Optional feature-detected integration

Objective: expose Mojo acceleration only where it is available and proven.

Tasks:

- Add runtime feature detection.
- Call Mojo only from private implementation details.
- Keep the public Python API unchanged.
- Keep Python fallback exercised in default tests.
- Record in generated benchmark/release metadata whether Mojo acceleration was used.

Exit criteria:

- Users without Mojo get identical behavior.
- Linux CI users with Mojo get measurable speedup.
- Windows local workflows still pass without Mojo.
- A single config or feature flag can disable Mojo.

### Stage 5: Expansion or archive decision

Objective: decide whether Mojo deserves more surface area.

Tasks:

- Expand only to the next measured bottleneck.
- Archive experiments that fail to beat simpler alternatives.
- Promote successful experiments into active conductor tracks and GitHub issues only after acceptance criteria pass.

Exit criteria:

- The repo either has one proven optional Mojo acceleration path or a documented decision not to continue.

## Runtime decision matrix

Every proposed Mojo migration must be evaluated against the current runtime and at least two realistic alternatives. Mojo should be chosen only when it is the best fit for the bottleneck, not because it is the newest option.

| Option | Best fit | Avoid when |
|---|---|---|
| Python with Rust-backed libraries | Default pipeline behavior, schema handling, orchestration, testability | Profiling shows tight CPU loops dominate runtime |
| Polars expressions/plugins | Columnar transforms, Parquet/Arrow-heavy operations, dataframe-native work | The logic is not naturally columnar or needs complex Python object behavior |
| Rust/PyO3/maturin | Stable compiled kernels, Windows support, packaging maturity | The implementation cost exceeds the measured runtime gain |
| Mojo | Isolated numeric or text kernels where Python interop is clean and benchmark wins are clear | Packaging, CI, fallback behavior, or legal-output parity is unresolved |
| DuckDB extensions | SQL-like analytical workloads and embedded reporting joins | The workload is not relational or extension maturity blocks reproducibility |
| LanceDB-native paths | Vector indexing, retrieval, and Arrow-native vector workflows | The bottleneck is pre-index extraction or post-query interpretation |
| vLLM/MAX/Transformers runtime changes | Model inference throughput and batching | The target is deterministic extraction, schema projection, or publication assembly |

Decision notes should record why rejected alternatives were not chosen. A short table in the relevant future conductor track is enough.

## Profiling and benchmark governance

Mojo work must start from measured bottlenecks.

Required evidence before opening an implementation track:

- A profiler result from `scalene`, `memray`, `py-spy`, `austin`, or an equivalent benchmark harness.
- A stable benchmark corpus with input hashes and expected output hashes.
- Baseline timings for current Python/Rust-backed behavior.
- A comparison against at least one non-Mojo acceleration path.
- A stated minimum improvement threshold before integration work begins.

Recommended benchmark corpus slices:

| Slice | Purpose | Required artifacts |
|---|---|---|
| Legislation extraction sample | Text normalization and provision/citation matching | Input hash, extracted spans, offset parity report |
| Large manifest projection | JSON/schema serialization and artifact generation | JSON schema validation, ordering parity, wall time |
| Vector retrieval fixture | Embedding/vector math and query post-processing | Recall fixture, tolerance report, timing |
| Publication review fixture | Rubric aggregation and report generation | Review JSON, Markdown output, blocker-label parity |

Benchmark artifacts should record OS, CPU/GPU, memory, Python version, Mojo version, dependency lockfile hash, input size, and command line.

## Interop, packaging, and CI strategy

Mojo should be introduced through optional feature detection only.

Preferred integration shape:

1. Python remains the canonical entrypoint.
2. Mojo kernels are private implementation details.
3. Import or runtime detection chooses Mojo only when available.
4. Python fallback is always exercised in default tests.
5. Optional CI validates Mojo on a supported Linux runner first.
6. Windows jobs validate fallback behavior and must not require Mojo.

Packaging rules:

- Do not add Mojo to required dependencies until Windows and CI support are proven for the intended profile.
- Do not publish artifacts whose behavior depends silently on Mojo availability.
- If Mojo acceleration is used, include that fact in benchmark and release metadata.
- Keep lockfile and environment changes scoped to an optional profile.

## Safety and correctness boundaries

Mojo is suitable for deterministic performance kernels. It is not a substitute for legal or policy judgment.

Do not migrate these areas without a separate correctness review:

- Legal reasoning or interpretation.
- Ontology design, policy classification, and semantic entailment.
- Citation validity judgments.
- Human-facing explanation text.
- Publication wording or review conclusions.

Any accelerated path that touches legal/NLP outputs must preserve traceability back to source text, offsets, labels, hashes, and review evidence.

## Exit and rollback criteria

Every Mojo experiment must have removal criteria before it starts.

Remove or freeze a Mojo experiment when any of these occur:

- It fails to beat the current implementation by the agreed threshold.
- Rust/PyO3, Polars, DuckDB, LanceDB, or existing Python libraries provide a simpler equivalent path.
- It blocks default GitHub Actions.
- It cannot provide deterministic Python fallback behavior.
- It complicates packaging or local Windows development beyond the measured value.
- It changes artifact schemas, ordering, offsets, or labels without an approved migration plan.

Rollback should be simple: disable feature detection, keep Python fallback as canonical, and remove optional CI/profile wiring in a single track.

## Roadmap lifecycle

Mojo support and packaging are moving targets, so this roadmap must be refreshed before it drives implementation work.

Review cadence:

- Re-check external state at least quarterly while Mojo remains unsupported on the default Windows workstation path.
- Re-check immediately before opening any Mojo conductor track.
- Update the `External state to track` section with the date, version, supported platforms, install method, and source links.
- Keep stale assumptions visible until they are replaced with new evidence.

Required review inputs:

- PyPI/package availability and supported wheel targets.
- Official documentation for Python interop, packaging, testing, and supported platforms.
- GitHub Actions runner support.
- License and redistribution terms.
- Local developer install path for Windows, WSL, Linux, and macOS.
- Compatibility with `pixi`, `uv`, lockfiles, and existing release packaging.

## Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| Windows support remains unavailable | Default local workflow cannot use Mojo | Keep Mojo optional and use Linux CI or WSL experiments at most |
| Packaging model changes | CI or release artifacts become brittle | Keep optional profiles isolated from default dependencies |
| Python interop overhead erases gains | Added complexity without measurable benefit | Benchmark end-to-end calls, not just kernel microbenchmarks |
| Legal output drift | Faster code changes offsets, labels, or traceability | Require artifact parity, source hashes, and review fixtures |
| Duplicate acceleration stacks accumulate | Repo becomes harder to maintain | Use the runtime decision matrix before each track |
| Experimental dependency slows CI | Default validation becomes less reliable | Keep Mojo jobs non-blocking until production gates pass |
| Licensing uncertainty | Distribution or deployment risk | Re-check license terms before experiments and before integration |

## Adoption scoring rubric

Before promoting any Mojo proposal into an implementation track, score it from 0 to 2 on each dimension.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Bottleneck evidence | No measured bottleneck | Local benchmark only | Reproducible profiler and benchmark evidence |
| Runtime benefit | No clear gain | Narrow microbenchmark gain | End-to-end workflow gain |
| Platform support | Unsupported on required paths | Optional Linux/macOS only | Compatible with required CI profile and fallback paths |
| Packaging cost | Requires default dependency churn | Optional profile with friction | Clean optional install and lockfile story |
| Correctness parity | Untested | Partial parity checks | Full artifact and behavioral parity |
| Maintainability | New specialist surface area | Small isolated kernel | Clear owner, tests, fallback, and removal path |

Promotion threshold:

- Score at least 9 out of 12.
- Score 2 for correctness parity.
- Score at least 1 for platform support.
- Document any dimension scoring below 2 in the future conductor track.

## Proposed future conductor tracks

These are roadmap items, not active tracks:

1. `track_mojo_readiness_audit_<date>`: verify OS support, licensing, packaging, GitHub Actions support, and candidate kernel shortlist.
2. `track_mojo_linux_ci_sandbox_<date>`: add optional `experiments/mojo/` kernels and non-blocking Linux CI.
3. `track_mojo_hotspot_benchmark_<date>`: extend benchmarks with Mojo candidates and compare against Rust/PyO3 and Polars plugins.
4. `track_mojo_optional_acceleration_<date>`: integrate one proven kernel behind optional feature detection and Python fallback.

## Track and GitHub issue promotion policy

This roadmap should not create active implementation work by itself. Promote work only when a concrete decision point exists.

Promotion rules:

- Create a conductor track for each future Mojo stage only when the previous stage's exit criteria are satisfied.
- Mirror promoted tracks into GitHub issues if the repo's project board is active.
- Label GitHub issues with `roadmap`, `runtime`, `performance`, and `mojo` where available.
- Include acceptance criteria copied from this roadmap rather than free-form implementation wishes.
- Close or archive a promoted track when evidence says Mojo is not the right tool for that stage.

Suggested issue fields:

| Field | Value |
|---|---|
| Status | Backlog until readiness gates are met |
| Priority | Medium if GitHub Actions runtime is a bottleneck; otherwise low |
| Area | Runtime / Performance |
| Risk | Experimental dependency |
| Evidence required | Profiling, benchmark, parity, CI, packaging, license |

## Current recommendation

Treat Mojo as a Linux GitHub Actions acceleration candidate. The first implementation work should be a readiness and hotspot benchmark track, followed by a non-blocking `experiments/mojo/` sandbox. Do not make Mojo a required dependency or touch legal-reasoning paths until a deterministic kernel proves a material end-to-end speedup with full artifact parity.
