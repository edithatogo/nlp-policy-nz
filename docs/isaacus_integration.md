# Isaacus Legal NLP Ecosystem Integration

Track 22 adds a repo-side integration scaffold for the Isaacus legal NLP
ecosystem. It records the Isaacus datasets, models, and tools that matter for
NZ legal NLP, normalises Australian legal rows into the existing pipeline schema,
and provides a starting point for NZ-MLEB retrieval benchmarks.

No Isaacus datasets, models, proprietary APIs, or checkpoints are downloaded by
this document or by the default scripts. External execution must be run in an
environment with explicit network/API access, local cache paths, and persisted
hashes for every downloaded artefact.

## Implemented Local Surfaces

- `src/nlp_policy_nz/training/isaacus_adapter.py` contains offline manifests,
  record normalisation, `PipelineRecord` conversion, NZ-MLEB query scaffolding,
  external-access gates, and report rendering.
- `scripts/download_isaacus_datasets.sh` prints the dataset/model/tool manifest
  for a download plan without performing network I/O. It defaults to `--audit`;
  `--live` is rejected by the repo-side wrapper.
- `scripts/evaluate_isaacus_models.sh` renders the integration report without
  calling model APIs or loading checkpoints. It defaults to `--audit`; `--live`
  is rejected by the repo-side wrapper.
- `tests/test_isaacus_adapter.py` covers required Isaacus assets, AU-to-pipeline
  normalisation, Maori macron preservation, MLEB relevance validation, and
  fail-closed external gates.
- `conductor/tracks/track22_isaacus_integration_20260613/external_gate_manifest.json`
  records the external download, API, model-evaluation, NZ-MLEB publication,
  semchunk comparison, and Blackstone Graph monitoring evidence required before
  live Isaacus integration is claimed.

## Script Access Boundary

The Track 22 shell wrappers are audit-only surfaces:

```sh
scripts/download_isaacus_datasets.sh --audit
scripts/evaluate_isaacus_models.sh --audit
```

Both wrappers set offline/no-telemetry environment guards before calling local
Python renderers. They do not clone repositories, download Hugging Face assets,
call proprietary APIs, evaluate models, train, or push artefacts. Passing
`--live` exits with code `64` and no stdout. Live execution belongs in a
separate approved lane with explicit cache paths, credentials, recorded hashes,
raw benchmark outputs, and publication evidence.

## Dataset Plan

| Dataset | Local status | External gate |
| --- | --- | --- |
| `isaacus/open-australian-legal-corpus` | Manifested and normalisable | Download 147K records, hash, convert to Parquet |
| `isaacus/open-australian-legal-qa` | Manifested | Download QA pairs and map to NZ QA template |
| `isaacus/legal-rag-bench` | Manifested | Download benchmark and map RAG outputs |
| `isaacus/mleb-legal-rag-bench` | Manifested | Extend with NZ legislation, Hansard, and decisions |

## Model And Tool Plan

| Asset | Local status | External gate |
| --- | --- | --- |
| `open-australian-legal-llm` | Manifested | Zero-shot NZ evaluation and AU-to-NZ transfer fine-tuning |
| `emubert` | Manifested | NZ encoding and document-similarity evaluation |
| `kanon-2-tokenizer` | Manifested | Maori token preservation comparison |
| `kanon-2-embedder` | Manifested as API/air-gapped | Credentialed retrieval evaluation |
| `semchunk` | Manifested for evaluation | Compare segmentation against `syntactic/chunking.py` |
| Blackstone Graph | Manifested for monitoring | Integrate only after stable upstream release |

## Current Recommendation

Use the Isaacus adapter as the import boundary for AU legal data and benchmark
metadata. Do not merge external AU corpora or replace embedding backends until
measured NZ benchmark outputs, raw JSONL results, and artefact hashes are
persisted.
