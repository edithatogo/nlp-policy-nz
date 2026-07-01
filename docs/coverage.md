# Coverage Gate

Track 23 sets the repository coverage threshold to 90 percent for the package
source tree.

The default gate measures `src/` with branch coverage enabled and writes both
terminal and XML reports:

```sh
pixi run python -m pytest -p no:tach -m "not benchmark" --cov=src --cov-report=term-missing --cov-report=xml
```

The coverage policy excludes only non-default execution surfaces that require
external runtime choices or optional vector backends:

- `src/nlp_policy_nz/semantic/finetune.py`
- `src/nlp_policy_nz/storage/faiss_adapter.py`
- `src/nlp_policy_nz/storage/haystack_pipeline.py`
- `src/nlp_policy_nz/training/run_qlora.py`

These files remain covered by targeted contract tests where practical, but they
do not count against the normal CI coverage threshold because they depend on
live training decisions or optional backend installations.

Benchmark tests are also excluded from the coverage gate. They run in the
dedicated benchmark workflows where timing variance and baseline comparisons
are handled separately.
