# Track 21: Bleeding-Edge Architecture Exploration for NZ Legal NLP

**Dependencies**: Track 20
**Parallelization Node**: Advanced Architecture Research
**Status**: Pending

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

## Files to Create/Modify

| File | Action |
|------|--------|
| `docs/architecture_comparison.md` | Create |
| `scripts/evaluate_mor.sh` | Create |
| `scripts/evaluate_mamba.sh` | Create |
| `scripts/evaluate_ttt.sh` | Create |
| `scripts/evaluate_diffusion_gemma.sh` | Create |
| `tests/test_architecture_eval.py` | Create |
| `src/nlp_policy_nz/training/eval_arch.py` | Create |
