# Recovered local worktree snapshots

This directory preserves substantive files recovered from two legacy, non-Git
copies found during the 2026-08-09 storage reconciliation:

- `issue105-runtime-matrix-copy/` came from `nlp-policy-nz-issue105`.
- `track34-publication-review-copy/` came from
  `nlp-policy-nz-track34-review`.

Only files whose exact Git blob was not reachable from the repository's
current remote refs were copied. Reproducible Pixi environments, Ruff and
pytest caches, Python bytecode, and generated test-output directories were
excluded.

These files are inert historical evidence. Their location does not restore
them to active runtime, Conductor, publication, or release state. In
particular, the archived claims and publication-protocol material do not prove
live Hugging Face, Zenodo, deployment, adoption, benchmark, or full-corpus
completion. Current repository status and hosted receipts remain authoritative.

The source directories can be removed after this archive is merged and the
GitHub-hosted tree is verified.
