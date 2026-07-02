# Track 72 Evidence

## Benchmark Harness

- Script: `scripts/track72_mojo_hotspot_benchmark.py`
- Test coverage: `tests/test_track72_mojo_hotspot_benchmark.py`
- Deterministic fixture: legislation-like modal-token scan over a fixed sentence corpus

## Local Validation

- `.\.venv\Scripts\python.exe scripts\track72_mojo_hotspot_benchmark.py --records 5 --iterations 1 --evidence .tmp\track72_mojo_hotspot_benchmark_smoke.json`
- `.\.venv\Scripts\python.exe -m pytest -p no:tach tests\test_track72_mojo_hotspot_benchmark.py -q`

## Decision

Mojo is not installed in the current local runtime, so the benchmark remains a deferred decision record. The harness still captures the current Python, `orjson`, and Polars baselines, records output hashes and environment metadata, and keeps Track 73 gated behind measurable Mojo evidence rather than assumption.

