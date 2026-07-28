# Citation Zenodo Mirroring Evidence

## Verified software release

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Tag | `v0.1.0` @ `41805da6c108cb70c29cf6890f35d3209543e763` |
| Zenodo version DOI | `10.5281/zenodo.21374372` |
| Zenodo concept DOI | `10.5281/zenodo.21374371` |
| Record | https://zenodo.org/records/21374372 |
| Verified at | 2026-07-28T14:43:00Z (API probe) |

## Hugging Face dataset pins

Pinned from `data/registry/huggingface_audit.json` into `mirror-manifest.json`
(`huggingface_revisions`). Software DOI and dataset revisions remain separate
citation surfaces.

## Validation

```text
pixi run --frozen -e py312 python scripts/check_citation_mirror.py
pixi run --frozen -e py312 pytest -p no:tach tests/test_citation_zenodo_mirror.py -q
```

## Boundary

OCR dataset DOI remains a separate registry gate (#166). This track covers the
software Zenodo mirror and citation metadata alignment only.
