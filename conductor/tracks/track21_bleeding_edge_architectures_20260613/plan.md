# Track 21: Bleeding-Edge Architecture Exploration for NZ Legal NLP

**Dependencies**: Track 20
**Parallelization Node**: Advanced Architecture Research
**Status**: In Progress

---

## Phase 1: MoR (Mixture-of-Recursions) — Highest Priority

**Estimated Effort**: High
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Clone `raymin0223/mixture_of_recursions`, set up conda env with torch 2.6.0 + flash-attn 2.7.4 | [ ] | |
| 1.2 | Download FineWeb-Edu dedup subset for baseline pre-training (SmolLM-Corpus) | [ ] | |
| 1.3 | Pre-train MoR 135M and 360M models on FineWeb-Edu + NZ legal corpus mixture | [ ] | |
| 1.4 | Evaluate routing behaviour: do deep recursions activate more on complex legal clauses? | [ ] | |
| 1.5 | Fine-tune MoR 360M on citation extraction; compare vs vanilla transformer baseline | [ ] | |
| 1.6 | Profile throughput and memory on full-Act (50K token) inputs | [ ] | |
| 1.7 | Push MoR-NZ checkpoints to Hugging Face Hub | [ ] | |

## Phase 2: TTT-Linear / TTT-RNN

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Find open-source TTT layer implementation (search HF Hub / GitHub) | [ ] | |
| 2.2 | Integrate TTT-Linear layer as spaCy component or standalone model | [ ] | |
| 2.3 | Evaluate perplexity scaling: TTT vs transformer on 2K / 8K / 32K / 128K NZ legal text | [ ] | |
| 2.4 | Fine-tune TTT-RNN for citation extraction; compare throughput vs transformer | [ ] | |

## Phase 3: Mamba-3 / SSD / SambaY

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Install Mamba-3/SSD via `pip install mamba-ssm`; verify CUDA kernel compilation | [ ] | |
| 3.2 | Evaluate Mamba-3 perplexity on NZ legal text; compare with transformer | [ ] | |
| 3.3 | Fine-tune Mamba-3 for citation extraction; measure throughput-accuracy tradeoff | [ ] | |
| 3.4 | Evaluate SambaY hybrid architecture on mixed-length benchmark | [ ] | |

## Phase 4: DiffusionGemma & Alternative Paradigms

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 4.1 | Download DiffusionGemma from Google; set up inference pipeline | [ ] | |
| 4.2 | Evaluate DiffusionGemma for legal text summarization (Bill → Summary) | [ ] | |
| 4.3 | Compare generation quality and speed vs autoregressive Gemma 3 | [ ] | |

## Phase 5: nex-agi & Frontier Models

**Estimated Effort**: Low-Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 5.1 | Download and evaluate **Nex-N2** zero-shot on NZ legal benchmark suite | [ ] | |
| 5.2 | Download and evaluate **MiniMax-01** on extreme long-context (256K+) legal task | [ ] | |
| 5.3 | Download and evaluate **NVIDIA Cosmos 3** / **Tencent HY-World 2.0** for legal reasoning | [ ] | |
| 5.4 | Evaluate **MiMo-V2.5** on mixed text/table legal documents | [ ] | |
| 5.5 | Monitor **DeVestral**, **TiRex**, **Ring**, **Ling** for repos/publication; evaluate if available | [ ] | |

## Phase 6: Architecture Comparison & Recommendation

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 6.1 | Run all evaluated architectures on shared NZ legal benchmark | [ ] | |
| 6.2 | Produce Pareto frontier plots: throughput vs citation F1, memory vs context length | [ ] | |
| 6.3 | Write `docs/architecture_comparison.md` with detailed analysis | [ ] | |
| 6.4 | Make recommendation: replace transformer backbone? If so, with which architecture? | [ ] | |
| 6.5 | Publish architecture evaluation dataset and results to Hugging Face | [ ] | |

## Phase 7: 2026 Emerging Architectures & Paradigms

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 7.1 | Evaluate **ModernBERT** (encoder replacement) for legal NER/citation extraction vs Legal-BERT baseline | [ ] | |
| 7.2 | Evaluate **Jamba 1.6** hybrid SSM-transformer for long-context legal document classification | [ ] | |
| 7.3 | Evaluate **Llama 4 / Gemma 3 MoE** routing behaviour on multi-task legal benchmark | [ ] | |
| 7.4 | Evaluate **RAG 2.0** dense retrieval + LLM reader vs current LanceDB embedding search for legal QA | [ ] | |
| 7.5 | Evaluate **DeepSeek-V3/R1** or Qwen3 MoE distilled variants for legal reasoning benchmarks | [ ] | |
| 7.6 | Assess **State Space Encoders** (Mamba-3 encoder variant) for legal sequence tagging vs BERT | [ ] | |
| 7.7 | Evaluate **Small Language Models** (<3B: Phi-3.5, Gemma 2B, Qwen2.5-1.5B) distilled on legal tasks for edge deployment | [ ] | |
| 7.8 | Evaluate **Test-Time Compute Scaling** (o1-style chain-of-thought) for complex legal reasoning: multi-statute interpretation, conflicting precedent resolution | [ ] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `docs/architecture_comparison.md` | Create |
| `scripts/evaluate_mor.sh` | Create |
| `scripts/evaluate_mamba.sh` | Create |
| `scripts/evaluate_ttt.sh` | Create |
| `scripts/evaluate_diffusion_gemma.sh` | Create |
| `tests/test_architecture_eval.py` | Create |
| `tests/test_track21_evidence.py` | Create |
| `tests/test_track21_script_contracts.py` | Create |
| `src/nlp_policy_nz/training/eval_arch.py` | Create |
| `src/nlp_policy_nz/training/track21_evidence.py` | Create |
| `conductor/tracks/track21_bleeding_edge_architectures_20260613/evidence.md` | Create |

## Implementation Note - 2026-06-21

Repo-side Track 21 harness is implemented:

- Added `src/nlp_policy_nz/training/eval_arch.py` for candidate registry,
  benchmark metrics, Pareto frontier selection, weighted ranking, recommendation,
  and Markdown report rendering.
- Added dry-run architecture entry points under `scripts/evaluate_*.sh`.
- Added `tests/test_architecture_eval.py` for registry, Pareto, ranking,
  recommendation, and report-scope contracts.
- Added `docs/architecture_comparison.md` with the provisional recommendation
  and explicit external training/checkpoint gates.

External MoR/TTT/Mamba/DiffusionGemma cloning, pretraining, fine-tuning,
profiling, and checkpoint publication remain pending until disk/GPU/model access
is available.

## Evidence Update - 2026-06-22

Current Track 21 bookkeeping separates repo-side dry-run comparison from
external model gates:

- Repo-side evidence is limited to the local candidate registry, deterministic
  example metrics, dry-run script surfaces, provisional architecture report, and
  tests that encode the acceptance-boundary contract.
- `evidence.md` is the track-local evidence boundary for this state and should
  be read before treating any Track 21 architecture recommendation as measured
  external benchmark evidence.
- External downloads, CUDA/GPU execution, third-party implementation installs,
  full benchmark measurements, raw profiler artefacts, checkpoint hashes, and
  Hugging Face publication remain pending.

The 2026-06-22 repo-side evidence lane also adds the
`Track21EvidenceReport` acceptance contract and focused tests so callers can
distinguish local dry-run evidence from external model-run gates.

## Validation Note - 2026-06-22

Focused repo-side Track 21 validation passed after integrating the evidence and
script-contract lanes:

- `python -B -m pytest -p no:cacheprovider -q tests\test_architecture_eval.py tests\test_track21_evidence.py tests\test_track21_script_contracts.py --basetemp C:\tmp\nlp-policy-nz-track21-final` passed: 10 tests.
- `python -m ruff check --no-cache src\nlp_policy_nz\training\eval_arch.py src\nlp_policy_nz\training\track21_evidence.py src\nlp_policy_nz\training\__init__.py tests\test_architecture_eval.py tests\test_track21_evidence.py tests\test_track21_script_contracts.py` passed.
- `python -B -m json.tool conductor\tracks\track21_bleeding_edge_architectures_20260613\metadata.json > nul` passed.
- `bash -n scripts/evaluate_mor.sh scripts/evaluate_mamba.sh scripts/evaluate_ttt.sh scripts/evaluate_diffusion_gemma.sh` passed.
- `bash scripts\evaluate_*.sh --audit` equivalents completed for MoR, Mamba-3, TTT-Linear, and DiffusionGemma without clone, download, training, or Hub push.

The local registry now covers the Track 21 candidate families in the spec,
including MoR/MoR-KV/DeVestral, TTT-Linear/TTT-RNN, Mamba-3/SSD/SambaY,
DiffusionGemma/GemmaDiffusion, nex-agi candidates, world-model candidates,
MiMo-V2.5, MiniMax-01, Ring, Ling, and TiRex. External model installation,
GPU-backed benchmark runs, measured Pareto evidence, and Hugging Face
publication remain pending.
