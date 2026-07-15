# Plan

GitHub issue: https://github.com/edithatogo/nlp-policy-nz/issues/104
Runtime-matrix issue: https://github.com/edithatogo/nlp-policy-nz/issues/105

- [x] Build an isolated spaCy 4 pre-release environment. (7cb73b2)
- [x] Reconcile `pyproject.toml`, `pixi.toml`, CI, and readiness docs around the supported Python matrix. (7cb73b2)
- [x] Run adapter, serialization, model, and extraction-contract tests. (7cb73b2; full extraction suite remains environment-blocked)
- [x] Benchmark against locked spaCy 3.8.14. (7cb73b2)
- [x] Check spaCy/Transformers/native-wheel compatibility and record failures. (7cb73b2)
- [x] Decide adopt, defer, or maintain a compatibility branch with evidence: defer adoption; retain spaCy 3.8.14. (7cb73b2)

## Review evidence (2026-07-14)

- Focused probe tests: `2 passed`.
- `uvx ruff check` and `uvx ruff format --check` passed for the new script and
  tests.
- Python 3.14 was explicitly tested: no spaCy 4 dev3 wheel exists, and the
  source build fails in `blis==0.7.11` Cythonization.
- Review fix `0f9c37f` corrected the documented spaCy 4 probe environment path.
- Production dependencies and lockfiles were unchanged; the defer decision is
  supported by the recorded native-wheel and adapter failures.
- Review fix `08cae6e` adds explicit entity-span output and a fixed deterministic
  benchmark workload to align the probe directly with the acceptance criteria.
