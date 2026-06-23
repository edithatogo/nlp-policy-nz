# Profiling

Track 19 adds repeatable wrappers for CPU and memory profiling of the processing
pipeline. The runners call the existing `nlp-policy-nz process` CLI so profiling
uses the same code path as normal corpus processing.

## Scalene

```bash
python scripts/profile_pipeline.py \
  --input data/hansard-sample \
  --output .tmp/profiling/hansard.parquet \
  --source hansard
```

The default report path is `docs/profiling/scalene.html`.
The wrapper also writes a JSON evidence note to
`docs/profiling/profile-pipeline-evidence.json` unless `--evidence` is set.

## Memray

```bash
python scripts/memray_trace.py \
  --input data/hansard-sample \
  --output .tmp/profiling/hansard.parquet \
  --source hansard
```

The default binary trace is `docs/profiling/memray.bin`, and the default
flamegraph is `docs/profiling/memray-flamegraph.html`.
The wrapper also writes a JSON evidence note to
`docs/profiling/memray-evidence.json` unless `--evidence` is set.

## Evidence Notes

The evidence notes are machine-readable run records. They include the command
line, return code, input path, report paths, Python executable, platform, and an
explicit `corpus_claim` field. A generated evidence note proves that a wrapper
was executed with the listed input; it does not prove a 1 GB or full-corpus run
unless the recorded input path and surrounding corpus inventory establish that
fact.

## Baseline Status

The full 6.5 GB Hansard baseline still requires the local source corpus. Record
the sample size, command, wall time, peak memory, and generated report paths here
after running the wrappers against that corpus.

Until that corpus is available, Track 19 treats profiling as an external gate:

- Scalene full-corpus gate: generate `docs/profiling/scalene.html` from at
  least 1 GiB of Hansard input.
- Memray full-corpus gate: generate `docs/profiling/memray.bin` and
  `docs/profiling/memray-flamegraph.html` from at least 1 GiB of Hansard input.
- Evidence must include the exact command, input byte count, wall time, peak
  memory, and artifact paths.
