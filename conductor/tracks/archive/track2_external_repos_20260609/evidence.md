# Track 2 Evidence - External Integrations and Data Sovereignty Registry

Track 2 is complete for repo-side integration scaffolding.

Implemented surfaces:

- `src/nlp_policy_nz/integrations/huggingface.py` provides Hugging Face dataset loading helpers with token lookup through `HF_TOKEN`.
- `src/nlp_policy_nz/integrations/zenodo.py` provides Zenodo Sandbox deposit, file upload, and publish helpers.
- `src/nlp_policy_nz/integrations/data_registry.py` provides `DataSovereigntyRegistry` and `DataRecord` for JSON-backed provenance records.
- `src/nlp_policy_nz/integrations/__init__.py` exposes the integration API from the package namespace.

Validation evidence:

- `tests/integration/test_integrations_zenodo.py` verifies Zenodo request construction with mocked HTTP calls.
- The Track 2 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Live Hugging Face dataset reads require network access and valid credentials when private or rate-limited datasets are used.
- Live Zenodo Sandbox or production deposits require explicit credentials and operator intent.
- Published DOI evidence remains outside this offline repo-side track.
