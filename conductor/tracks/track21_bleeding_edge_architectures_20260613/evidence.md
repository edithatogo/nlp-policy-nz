# Track 21 Evidence Boundary - 2026-06-22

This note records the current Track 21 evidence boundary. It is a repo-side
documentation/bookkeeping update only; it does not claim external model
downloads, GPU training, checkpoint publication, or live benchmark execution.

## Repo-side dry-run evidence

The following surfaces are present in the working tree and support local,
bounded architecture-comparison dry runs:

- `src/nlp_policy_nz/training/eval_arch.py` defines the architecture candidate
  registry, comparable metrics, Pareto-frontier selection, weighted ranking,
  recommendation logic, and Markdown report rendering.
- `src/nlp_policy_nz/training/track21_evidence.py` defines the deterministic
  acceptance contract that separates repo-side dry-run evidence from external
  GPU/model/Hugging Face gates.
- `tests/test_architecture_eval.py` describes the expected repo-side contracts,
  including explicit separation between repo-side evidence and external model
  gates.
- `docs/architecture_comparison.md` documents the provisional architecture
  comparison and states that the recommendation is based on deterministic
  dry-run/example metrics, not measured production training runs.
- `scripts/evaluate_mor.sh`, `scripts/evaluate_ttt.sh`,
  `scripts/evaluate_mamba.sh`, and `scripts/evaluate_diffusion_gemma.sh` are
  dry-run entry points for architecture-family setup and evaluation workflows.

These items are sufficient evidence that the repository can express a
deterministic comparison contract and provisional recommendation without
performing heavyweight external operations.

## External gates not satisfied

The following Track 21 acceptance gates remain external and are not satisfied by
the repo-side dry-run evidence:

- Clone, pin, and install third-party MoR, TTT, Mamba/SSM, and DiffusionGemma
  implementations in a controlled environment.
- Download FineWeb-Edu, NZ legal benchmark shards, model weights, tokenizer
  assets, or other large external datasets.
- Run CUDA/GPU validation, pretraining, fine-tuning, profiler traces, or
  measured throughput/memory/perplexity/citation-F1 benchmarks.
- Capture raw measured benchmark JSONL, profiler artefacts, checkpoint hashes,
  and qualitative legal-review notes.
- Publish model checkpoints, datasets, or architecture evaluation outputs to
  Hugging Face or another remote registry.

## Current status

Track 21 is repo-side documented but externally gated. The deterministic
dry-run comparison can support planning and review; it must not be used as
evidence that any architecture has completed measured NZ legal benchmark
evaluation or is ready to replace the transformer backbone in production.
