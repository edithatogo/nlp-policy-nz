# Track 59: Polars-Native Corpus Pipeline Substitution

## Overview

Track 59 replaces the hottest tabular corpus-browser paths with a Polars-native
core while keeping the public Gradio-facing API stable. The goal is to use
Polars where it materially improves local performance and data portability,
without changing the user-facing pandas boundary until a later track proves a
full switch is worthwhile.

## Requirements

- Inventory the current tabular hot paths used by the corpus browser.
- Implement at least two stable Polars-native substitutions behind the current
  public API surface.
- Keep `spaces/app.py` returning pandas DataFrames and plain Python values so
  the UI contract does not change.
- Benchmark the pandas baseline against the Polars candidate paths.
- Record which dataframe surfaces are Polars-only, hybrid, or pandas-only in
  the dependency policy matrix.
- Preserve Windows and GitHub Actions compatibility.

## Acceptance Criteria

- `load_parquet` and `search_chunks` use a Polars-native core internally.
- `compute_stats` remains pandas-first unless a later benchmark justifies moving
  that smaller aggregation off the simpler path.
- The public app boundary still returns pandas DataFrames and dicts.
- Parity tests confirm the Polars core matches the existing behaviour on sample
  fixtures.
- A benchmark script records baseline-versus-candidate evidence and a
  recommendation for each hot path.
- The dependency policy matrix records the dataframe surface boundary.
- The Conductor registry, GitHub issue mirror, and GitHub project fields are
  updated when the work is complete.

## Out of Scope

- Removing pandas from the UI boundary.
- Migrating graph, citation, or publication chart rendering to Polars.
- Introducing new runtime services or non-local storage backends.
