# Plan

GitHub issue: https://github.com/edithatogo/nlp-policy-nz/issues/103 (closed)

- [x] Correct `CITATION.cff` and add `.zenodo.json`.
- [x] [HUMAN] Publish/verify Zenodo releases and pin Hugging Face revisions.
- [x] Add the repository mirror manifest with an explicit no-DOI claim boundary (superseded by verified DOIs after live record check).

## Evidence

- `CITATION.cff` and `.zenodo.json` both describe `nlp-policy-nz` version
  `0.1.0` and the same GitHub repository.
- Live Zenodo record verified: version DOI `10.5281/zenodo.21374372`,
  concept DOI `10.5281/zenodo.21374371`, record
  https://zenodo.org/records/21374372 (published 2026-07-15).
- Immutable tag `v0.1.0` at commit `41805da6c108cb70c29cf6890f35d3209543e763`.
- Hugging Face dataset revisions pinned in `mirror-manifest.json` from
  `data/registry/huggingface_audit.json`.
- Offline contract: `scripts/check_citation_mirror.py` /
  `tests/test_citation_zenodo_mirror.py`.
