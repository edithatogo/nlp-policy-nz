# Track 21: Bleeding-Edge Architecture Exploration for NZ Legal NLP

**Dependencies**: Track 20 (Fine-Tuning Pipeline)
**Parallelization Node**: Advanced Architecture Research
**Status**: Complete (repo-side; live model gates external)

---

## Goal

Explore, evaluate, and (where feasible) fine-tune the most promising bleeding-edge model architectures on NZ legal/Hansard data. Targets architectures offering step-change improvements in efficiency, context length, or reasoning over standard transformers.

## Architecture Candidates

### Cluster A: Recursive & Adaptive Computation

| Architecture | Paper/Source | Innovation | NZ Legal Relevance |
|-------------|--------------|------------|-------------------|
| **MoR (Mixture-of-Recursions)** | NeurIPS 2025 / github.com/raymin0223 | Recursive Transformer with adaptive per-token depth routing; 2× throughput improvement | Long legislative docs benefit from adaptive depth — simple sections exit early, complex clauses get deeper processing |
| **MoR KV-sharing variant** | Same paper | Reuses KV pairs across recursions, reduces prefill latency | Critical for processing full Acts (>50K tokens) on limited GPU |
| **DeVestral** | Community | Recursive depth architecture | Monitor for NZ legal application |

### Cluster B: Test-Time Training & Recurrent Alternatives

| Architecture | Paper/Source | Innovation | NZ Legal Relevance |
|-------------|--------------|------------|-------------------|
| **TTT-Linear** | TTT Layers (ICML 2024) | Replaces attention with linear model updated at test time; O(n) scaling | Full-Act processing on consumer GPUs |
| **TTT-RNN** | TTT Layers | RNN variant; strong on long-range dependencies | Debate tracking across months/years of Hansard |
| **Mamba-3** | SSM v3 | Selective state space model; linear-time sequence modeling | Efficient long-document encoding |
| **SSD (State Space Duality)** | Mamba-2 | Unified SSM + attention view; enables hybrids | Best of both worlds for NZ mixed documents |
| **SambaY** | Hybrid SSM-Attention | Mamba layers + sliding-window attention | Efficient for mixed-length NZ documents |

### Cluster C: Diffusion & Alternative Generation

| Architecture | Innovation | NZ Relevance |
|-------------|------------|-------------|
| **DiffusionGemma** (Google) | Diffusion-based LM via iterative denoising | Legal text generation / summarization |
| **GemmaDiffusion** (Community) | Fine-tuning DiffusionGemma | Clause summarization and explanation |

### Cluster D: Frontier Labs & Multimodal

| Architecture | Source | Innovation | NZ Relevance |
|-------------|--------|------------|-------------|
| **Nex-N2** | nex-agi (Shanghai Innovation Inst.) | SOTA open-source LLM | Cross-lingual legal concept transfer |
| **NexRL** | nex-agi | Ultra-loosely-coupled LLM post-training (RL) | Post-tune fine-tuned models with RL from legal feedback |
| **NexAU** | nex-agi | Agent framework for tool-using agents | Agent orchestrator for legal document workflows |
| **NVIDIA Cosmos 3** | NVIDIA | World foundation model | Legal causal chain reasoning |
| **Tencent HY-World 2.0** | Tencent | Large world model | Cross-modal legal dataset understanding |
| **MiMo-V2.5** | Mixture of Modalities | Text + tables + structured data | Legal docs contain schedules and provisions |
| **MiniMax-01** | MiniMax | 456B MoE, 4M context | Extreme long-doc omnibus bill analysis |
| **Ring** | Community | Ring attention for distributed context | Extreme long-context distributed inference |
| **Ling** | Community | Lightweight architecture | Edge deployment of legal NLP |
| **TiRex** | Community | Tiled Recursive architecture | Hierarchical legal document processing |


## Training Approach

- **MoR**: Install from `raymin0223/mixture_of_recursions`, pre-train + fine-tune on NZ legal corpus (135M-1.7B scale). Evaluate routing behaviour on legal vs general text.
- **TTT-Linear/RNN**: Use open-source implementations, fine-tune on long-document tasks. Evaluate perplexity on full-Act text.
- **Mamba-3/SSD**: Use `mamba` package, fine-tune for citation extraction. Compare speed/accuracy vs transformer baselines.
- **DiffusionGemma**: Evaluate for legal summarization. Compare against autoregressive baselines.
- **nex-agi models (Nex-N2)**: Download and evaluate zero-shot on NZ legal tasks; fine-tune if promising.

## Evaluation Framework

| Dimension | Metric | Target |
|-----------|--------|--------|
| Throughput | Tokens/sec on 50K token input | >2× vs transformer baseline |
| Memory | Peak GPU memory (GB) for full-Act processing | <48GB (single A100) |
| Citation F1 | Token-level citation extraction | >90% F1 |
| Perplexity | Perplexity on held-out NZ legal text | Lower is better |
| Context Scaling | Perplexity at 8K / 32K / 128K tokens | Stable across all lengths |
| Māori Token Integrity | % of Māori words preserved as single tokens | >95% |

## Acceptance Criteria

- [x] Repo-side architecture registry, deterministic comparison harness, audit-only script entry points, and evidence helpers are implemented and tested.
- [x] Architecture comparison report published in `docs/architecture_comparison.md` with provisional recommendation boundaries.
- [x] External model/setup/benchmark/publication gates are captured in `external_gate_manifest.json` so measured claims are explicit and auditable.
- [ ] MoR architecture installed and training pipeline functional on NZ legal data.
- [ ] At least 3 bleeding-edge architectures evaluated on NZ legal benchmark with measured external runs.
- [ ] One architecture identified as best-performing on measured throughput-accuracy Pareto frontier.
- [ ] Recommendations for production replacement of transformer backbone are backed by measured external benchmark evidence.

## Repo-side Evidence Boundary - 2026-06-22

The repository now contains a deterministic dry-run architecture comparison
harness and a Track 21 acceptance/evidence contract. These local surfaces
support planning, review, and provisional documentation only. Track 21 is
repo-side complete when paired with `external_gate_manifest.json`; live
architecture setup, GPU/model runs, measured NZ legal benchmark outputs, and
publication evidence remain external gates.
