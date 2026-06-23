# Bleeding-Edge Architecture Comparison

Track 21 now has a repo-side evaluation harness for comparing non-standard
language-model backbones on NZ legal tasks. The local harness records candidate
metadata, normalises benchmark metrics, computes the throughput-accuracy Pareto
frontier, and renders a Markdown recommendation report.

External training and checkpoint publication remain gated on model downloads,
GPU capacity, benchmark artefact storage, and remote registry credentials. No
live pretraining, fine-tuning, or checkpoint publication is claimed by this
document.

## Candidate Registry

| ID | Family | NZ legal rationale | Tasks |
| --- | --- | --- | --- |
| `mor` | mixture-of-recursions | Promising for long Acts and Bills where simple clauses need less compute than amendment-heavy provisions. | nz-legal-citation, legislation-summarisation, policy-qa |
| `ttt-linear` | test-time-training | Candidate for session-specific adaptation to inquiry packs, submissions, and legislative histories. | policy-qa, long-context-retrieval, nz-legal-citation |
| `mamba-3` | state-space | Strong throughput candidate for large corpus indexing and long statutory context windows. | nz-legal-citation, long-context-retrieval, policy-qa |
| `diffusion-gemma` | diffusion-language-model | Useful comparison point for accuracy-sensitive drafting, but likely slower for interactive legal research. | legislation-summarisation, drafting-quality, policy-qa |

## Implemented Harness

- `src/nlp_policy_nz/training/eval_arch.py` defines architecture candidates,
  comparable benchmark metrics, Pareto frontier selection, weighted ranking, and
  Markdown report rendering.
- `scripts/evaluate_mor.sh`, `scripts/evaluate_ttt.sh`,
  `scripts/evaluate_mamba.sh`, and `scripts/evaluate_diffusion_gemma.sh`
  provide audit-only entry points for each architecture family. They default to
  deterministic repo-side reports, set offline model-download environment flags,
  and reject `--live` with exit code 64 so clone/download/train/publish work
  cannot start from these wrappers by accident.
- `tests/test_architecture_eval.py` covers the registry, Pareto filtering,
  ranking, recommendation, and report scope language.

## Current Recommendation

Using the deterministic dry-run example metrics in the harness, `mamba-3` is the
current throughput-accuracy frontier candidate for transformer-backbone
replacement. It combines the highest example throughput, lowest example memory
use, and longest context window while remaining above the NZ legal citation and
Maori-token-integrity gates.

This recommendation is provisional. Before replacing a transformer backbone,
the project should rerun the harness with measured benchmark outputs from at
least three external architecture runs and persist the raw JSONL, profiler
traces, and checkpoint hashes.

## Remaining External Gates

- Open a separate reviewed live lane before cloning and pinning the MoR, TTT,
  Mamba, or DiffusionGemma implementations.
- Download or prepare FineWeb-Edu and NZ legal benchmark shards only in an
  environment with sufficient disk capacity and an explicit live-run record.
- Run training, fine-tuning, profiler, and qualitative legal-review passes from
  that live lane, not from the repo-side audit wrappers.
- Publish checkpoint manifests only after raw metrics and hashes are captured.
