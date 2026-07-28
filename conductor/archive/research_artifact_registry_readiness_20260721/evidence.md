# Evidence — research_artifact_registry_readiness_20260721

## Validation commands

```powershell
$env:CI='true'; pixi run --frozen -e py312 pytest -p no:tach tests/test_registry_readiness_contract.py tests/test_registry_huggingface_audit.py tests/test_registry_ocr_artifact.py tests/test_registry_ontology_submission_gate.py -q
pixi run --frozen -e py312 python scripts/check_registry_readiness.py
pixi run --frozen -e py312 ruff check scripts/check_registry_readiness.py scripts/check_ocr_artifact_registry.py scripts/check_ontology_submission_gate.py scripts/audit_huggingface_targets.py tests/test_registry_*.py
```

Optional live Hugging Face Croissant probe (not used in default CI):

```powershell
pixi run --frozen -e py312 python scripts/audit_huggingface_targets.py --network
```

## Repository artefacts

| Artefact | Issue | Checker |
| --- | --- | --- |
| `data/registry/ocr_artifact.json` | #166 | `scripts/check_ocr_artifact_registry.py` |
| `data/registry/huggingface_audit.json` | #167 | `scripts/audit_huggingface_targets.py` |
| `data/registry/ontology_submission_gate.json` | #168 | `scripts/check_ontology_submission_gate.py` |

Aggregate contract: `scripts/check_registry_readiness.py` and `docs/registry-readiness.md`.

## External boundaries

- **OCR DOI (#166):** `ocr_artifact.json` status is `metadata_complete_doi_pending`; `doi` and `deposit_url` remain null. No Zenodo publication claim is made until an authoritative versioned DOI is verified externally.
- **Hugging Face (#167):** Repo-side audit records revision-pinned card and Croissant evidence. Default CI validates the local audit JSON only; live endpoint probes require `--network`.
- **Ontology registry (#168):** `submission_status` is `no_submission`; `registry_response` is null. Candidate namespace is a placeholder; no external ontology registry acceptance is sought or claimed.
