# Track 57 Evidence: DSPy Program Optimization for Legal NLP

## Acceptance Status

- repo_side_contracts: satisfied
- dependency_documented: satisfied
- optimizer_experiment: satisfied
- source_anchors: satisfied
- review_metadata: satisfied
- decision_contract: satisfied
- review_ready: satisfied

## Measurements

- Signature count: 3
- Optimizer experiments: 1
- Evaluation examples: 3
- Source anchor coverage: 1.00
- Review metadata coverage: 1.00
- Dependency state: rejected
- Recommendation written: True
- Rollback steps recorded: True
- Docs present: True

## Decision Record

DSPy is rejected as a required repository dependency. The repo-side evidence
shows that the same three legal NLP signatures can be exercised with a
deterministic evaluation harness, and the synthetic optimizer experiment does
not justify adding a new default runtime dependency.

## Validation

- `.\\.venv\\Scripts\\python.exe -m pytest -p no:tach -q tests\\test_track57_dspy_optimization.py`
- `.\\.venv\\Scripts\\python.exe -m ruff check src\\nlp_policy_nz\\training\\track57_dspy.py src\\nlp_policy_nz\\training\\__init__.py tests\\test_track57_dspy_optimization.py`

## Rollback

1. Remove the optional Track 57 helper module if it is no longer needed.
2. Keep the deterministic eval fixtures and baseline templates in the repo.
3. Re-run the Track 57 evidence tests before changing dependency policy again.

