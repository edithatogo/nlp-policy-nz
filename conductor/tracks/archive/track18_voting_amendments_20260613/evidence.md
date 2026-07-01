# Track 18 evidence

## Repo-side implementation

- `src/nlp_policy_nz/parliament/voting.py` parses Hansard division text into motion, aye/nay/abstain counts, member votes, party tallies, and outcome.
- `src/nlp_policy_nz/parliament/amendments.py` parses amendment records, detects SOP/technical/substantive amendment types, diffs XML/JSON bill versions, and builds amendment lifecycle graphs.
- `src/nlp_policy_nz/parliament/__init__.py` exposes the Track 18 parser API.
- `src/nlp_policy_nz/storage/serialization.py` adds `voting_record` and `amendments` to `PipelineRecord` and dataframe/parquet conversion.
- `src/nlp_policy_nz/pipeline_api.py` extracts Track 18 fields during pipeline processing.
- `src/nlp_policy_nz/api/server.py` includes voting and amendment fields in inline processing responses.
- `src/nlp_policy_nz/cli/main.py` exposes `voting-summary` and `amendment-history`.
- `tests/test_voting.py` covers division parsing and MP party lookup.
- `tests/test_amendments.py` covers amendment parsing, bill diffing, lifecycle graphs, schema integration, pipeline extractors, and CLI commands.

## Review fixes

- Added the missing Conductor track index.
- Updated the specification from pending to repo-side complete.
- Kept corpus-wide >95% parser accuracy as an external evaluation gate rather than overclaiming benchmark accuracy from fixture-driven tests.

## Verification

- `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_voting.py tests\test_amendments.py --basetemp C:\tmp\nlp-policy-nz-track18-review` -> 15 passed.
- `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\parliament\voting.py src\nlp_policy_nz\parliament\amendments.py src\nlp_policy_nz\parliament\__init__.py tests\test_voting.py tests\test_amendments.py src\nlp_policy_nz\pipeline_api.py src\nlp_policy_nz\storage\serialization.py` -> passed.

## Residual external gate

- Measured >95% division parsing accuracy requires a curated Hansard division benchmark or a documented sample from `corpus-nz-hansard`.
