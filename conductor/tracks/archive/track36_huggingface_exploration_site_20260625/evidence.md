# Track 36 Evidence

## Implemented Space Surface

- `spaces/app.py` now exposes fixture-backed Track 36 pages for overview, corpus statistics, ontology coverage, graph/vector outputs, generated artifacts, publication protocol, and uploaded Parquet browsing.
- `spaces/README.md` documents fixture mode, optional full-data Parquet exploration, deployment expectations, and CI-friendly smoke tests.
- `spaces/requirements.txt` remains the Hugging Face Space dependency source for Gradio, pandas, Plotly, and Parquet support.

## Source Inputs

- Track 32 checked-in statistics under `data/statistics/`.
- Track 33 checked-in graph/vector outputs under `data/analysis/`.
- Track 34 checked-in publication protocol under `data/publication/` and `docs/publication_protocol.md`.
- Track 35 checked-in publication artifacts under `artifacts/`.

## Validation

- `pixi run python -m pytest -q tests\test_gradio_space.py`

## Blocker Boundary

The Space defaults to deterministic fixture mode. Full-corpus statistics, graph/vector claims, live Hugging Face publication evidence, and LanceDB-backed exploration remain gated until canonical full-corpus exports, credentials, or mounted data are supplied.
