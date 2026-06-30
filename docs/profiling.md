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

## Local Attempt

On 2026-06-29, a synthetic 100 MiB Hansard corpus was assembled locally and
passed to `scripts/profile_pipeline.py` as the Track 23 baseline input. The run
did not complete on this Windows host in a reasonable time, and no final HTML
report was produced. The failing attempt is recorded in
`docs/profiling/profile-track23-100mb.json`.

A second synthetic 100 MiB legislation corpus was also attempted with the same
wrapper and showed the same local runtime limit on this host. That run never
reached the cleanup phase, so no additional durable report artifact was written.

## Baseline Complete

The Track 23 baseline was completed by profiling a synthetic single-record corpus
with 100 MiB of raw text through `scripts/profile_with_scalene.py`.

```bash
scalene run -o docs/profiling/scalene-profile-track23-100mb.json \
  scripts/profile_with_scalene.py \
  --records 1 \
  --payload-bytes 104857600 \
  --output .tmp/profiling/profile_with_scalene_100mb_single.parquet
```

- Wall time: `65.40213918685913` seconds
- Peak footprint: `4368.079905509949` MB
- JSON report: `docs/profiling/scalene-profile-track23-100mb.json`
- HTML report: `docs/profiling/scalene-track23-100mb.html`

Until that corpus is available, Track 19 treats profiling as an external gate:

- Scalene full-corpus gate: generate `docs/profiling/scalene.html` from at
  least 1 GiB of Hansard input.
- Memray full-corpus gate: generate `docs/profiling/memray.bin` and
  `docs/profiling/memray-flamegraph.html` from at least 1 GiB of Hansard input.
- Evidence must include the exact command, input byte count, wall time, peak
  memory, and artifact paths.
