# Bleeding-Edge Architecture Comparison

Track 21 has a repo-side evaluation harness for comparing non-standard
language-model backbones on NZ legal tasks. The local harness records candidate
metadata, normalises benchmark metrics, computes a throughput-accuracy Pareto
frontier, ranks candidates, and renders a Markdown recommendation report.

External training and checkpoint publication remain gated on model downloads,
third-party implementation pinning, GPU or equivalent validated runtime
capacity, raw benchmark artefact storage, and remote registry credentials. No
live pretraining, fine-tuning, measured benchmark, or checkpoint publication is
claimed by this document.

## Candidate registry

The registry in `src/nlp_policy_nz/training/eval_arch.py` covers the Track 21
architecture families:

- Recursive and adaptive compute: MoR, MoR KV-sharing, DeVestral, TiRex.
- Test-time training and recurrent alternatives: TTT-Linear, TTT-RNN.
- State-space and hybrid sequence models: Mamba-3, SSD, SambaY.
- Diffusion and alternative generation: DiffusionGemma, GemmaDiffusion.
- Frontier and post-training systems: Nex-N2, NexRL, NexAU.
- World and multimodal candidates: NVIDIA Cosmos 3, Tencent HY-World 2.0,
  MiMo-V2.5.
- Extreme-context and deployment patterns: MiniMax-01, Ring attention, Ling.

Phase 7 candidates, including ModernBERT, Jamba 1.6, Llama 4/Gemma 3 MoE, RAG
2.0, DeepSeek/Qwen MoE variants, state-space encoders, small language models,
and test-time compute scaling, are represented as external evaluation gates and
metadata-level monitoring targets until concrete implementations and benchmark
artefacts are pinned.

## Implemented harness

- `src/nlp_policy_nz/training/eval_arch.py` defines architecture candidates,
  comparable benchmark metrics, Pareto frontier selection, weighted ranking,
  and Markdown report rendering.
- `src/nlp_policy_nz/training/track21_evidence.py` defines the acceptance
  contract that separates repo-side evidence from external model-run gates.
- `scripts/evaluate_mor.sh`, `scripts/evaluate_ttt.sh`,
  `scripts/evaluate_mamba.sh`, and `scripts/evaluate_diffusion_gemma.sh`
  provide audit-only entry points. They default to deterministic repo-side
  reports, set offline model-download flags, and reject `--live` with exit code
  64 so clone, download, train, and publish work cannot start by accident.
- `conductor/archive/track21_bleeding_edge_architectures_20260613/external_gate_manifest.json`
  records the live setup, measured benchmark, profiler, recommendation, and Hub
  publication evidence required before Track 21 claims production-grade model
  results.
- `tests/test_architecture_eval.py`, `tests/test_track21_evidence.py`,
  `tests/test_track21_script_contracts.py`, and
  `tests/test_track21_external_gate_manifest.py` cover the registry, Pareto
  filtering, ranking, recommendation, evidence boundaries, script safety, and
  manifest contract.

## Current recommendation

Using the deterministic dry-run example metrics in the harness, `mamba-3` is the
current provisional throughput-accuracy frontier candidate for transformer
backbone replacement. It combines the highest example throughput, lowest example
memory use, and longest context window while remaining above the NZ legal
citation and Maori-token-integrity gates.

This recommendation is not a production replacement decision. Before replacing a
transformer backbone, the project must rerun the harness with measured benchmark
outputs from at least three external architecture runs and persist raw JSONL,
profiler traces, implementation commits, dependency locks, checkpoint hashes,
and qualitative review notes.

## Remaining external gates

- Pin and install at least three third-party architecture implementations in a
  reviewed live lane.
- Download or prepare FineWeb-Edu and NZ legal benchmark shards only in an
  environment with sufficient disk capacity and an explicit live-run record.
- Run training, fine-tuning, profiler, context-scaling, and qualitative
  legal-review passes from that live lane, not from the repo-side audit wrappers.
- Produce measured Pareto artefacts for throughput versus citation F1 and memory
  versus context length.
- Publish evaluation datasets, model cards, or checkpoint manifests only after
  raw metrics and hashes are captured.
