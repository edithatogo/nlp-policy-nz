"""Repo-side evaluation helpers for bleeding-edge policy-model architectures."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True)
class ArchitectureCandidate:
    """A model architecture candidate to evaluate against NZ legal tasks."""

    id: str
    name: str
    family: str
    source: str
    innovation: str
    nz_legal_relevance: str
    tasks: tuple[str, ...]
    status: str = "planned"
    external_dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class ArchitectureMetrics:
    """Comparable metrics for NZ legal benchmark evaluation."""

    tokens_per_second: float
    peak_memory_gb: float
    citation_f1: float
    perplexity: float
    max_context_tokens: int
    maori_token_integrity: float
    notes: str = ""


@dataclass(frozen=True)
class ArchitectureEvaluation:
    """A measured architecture result on one benchmark split."""

    architecture_id: str
    benchmark_name: str
    metrics: ArchitectureMetrics
    baseline_id: str | None = None


def default_architecture_registry() -> dict[str, ArchitectureCandidate]:
    """Return the Track 21 candidate registry without importing heavy ML stacks."""
    candidates = [
        ArchitectureCandidate(
            id="mor",
            name="Mixture of Recursions",
            family="mixture-of-recursions",
            source="raymin0223/mixture_of_recursions",
            innovation="Recursive depth routing for adaptive compute allocation.",
            nz_legal_relevance=(
                "Promising for long Acts and Bills where simple clauses need "
                "less compute than amendment-heavy provisions."
            ),
            tasks=("nz-legal-citation", "legislation-summarisation", "policy-qa"),
            external_dependencies=("FineWeb-Edu", "GPU pretraining run", "checkpoint host"),
        ),
        ArchitectureCandidate(
            id="mor-kv",
            name="MoR KV-Sharing Variant",
            family="mixture-of-recursions",
            source="raymin0223/mixture_of_recursions",
            innovation="Recursive depth routing with KV reuse across recursions.",
            nz_legal_relevance=(
                "Targets lower prefill latency for full-Act processing when many "
                "clauses share context across recursive passes."
            ),
            tasks=("long-context-retrieval", "policy-qa", "nz-legal-citation"),
            external_dependencies=("MoR checkpoint", "GPU profiler", "KV-cache traces"),
        ),
        ArchitectureCandidate(
            id="devestral",
            name="DeVestral",
            family="recursive-depth",
            source="community recursive-depth implementations",
            innovation="Recursive-depth architecture under community monitoring.",
            nz_legal_relevance=(
                "Potential fallback recursive-depth comparator if public "
                "implementations mature enough for legal benchmark runs."
            ),
            tasks=("policy-qa", "long-context-retrieval"),
            status="monitor",
            external_dependencies=("public repository", "model weights"),
        ),
        ArchitectureCandidate(
            id="ttt-linear",
            name="Test-Time Training Linear Attention",
            family="test-time-training",
            source="TTT linear-attention research implementations",
            innovation="Hidden-state adaptation at inference time for long context.",
            nz_legal_relevance=(
                "Candidate for session-specific adaptation to inquiry packs, "
                "submissions, and legislative histories."
            ),
            tasks=("policy-qa", "long-context-retrieval", "nz-legal-citation"),
            external_dependencies=("TTT implementation", "long-context benchmark shard"),
        ),
        ArchitectureCandidate(
            id="ttt-rnn",
            name="Test-Time Training RNN",
            family="test-time-training",
            source="TTT layer research implementations",
            innovation="RNN-style test-time adaptation for linear sequence scaling.",
            nz_legal_relevance=(
                "Useful comparator for debate tracking across extended Hansard "
                "timelines and recurring procedural language."
            ),
            tasks=("nz-legal-citation", "long-context-retrieval", "policy-qa"),
            external_dependencies=("TTT-RNN implementation", "GPU benchmark host"),
        ),
        ArchitectureCandidate(
            id="mamba-3",
            name="Mamba-3 State Space Model",
            family="state-space",
            source="Mamba SSM research lineage",
            innovation="Linear-time sequence modelling with recurrent state.",
            nz_legal_relevance=(
                "Strong throughput candidate for large corpus indexing and "
                "long statutory context windows."
            ),
            tasks=("nz-legal-citation", "long-context-retrieval", "policy-qa"),
            external_dependencies=("Mamba-compatible runtime", "GPU benchmark host"),
        ),
        ArchitectureCandidate(
            id="ssd",
            name="State Space Duality",
            family="state-space-hybrid",
            source="Mamba-2/SSD research lineage",
            innovation="Unifies SSM and attention views for hybrid sequence modelling.",
            nz_legal_relevance=(
                "Promising for mixed statutory text where local citation spans and "
                "long-range provision references both matter."
            ),
            tasks=("nz-legal-citation", "entity-linking", "policy-qa"),
            external_dependencies=("SSD implementation", "GPU benchmark host"),
        ),
        ArchitectureCandidate(
            id="sambay",
            name="SambaY",
            family="state-space-attention-hybrid",
            source="hybrid SSM-attention research implementations",
            innovation="Mamba-style layers combined with sliding-window attention.",
            nz_legal_relevance=(
                "Candidate for documents with short clauses embedded in long "
                "schedules, appendices, and legislative histories."
            ),
            tasks=("long-context-retrieval", "nz-legal-citation", "policy-qa"),
            external_dependencies=("SambaY implementation", "mixed-length benchmark"),
        ),
        ArchitectureCandidate(
            id="diffusion-gemma",
            name="DiffusionGemma",
            family="diffusion-language-model",
            source="Diffusion language model research lineage",
            innovation="Iterative denoising objective for text generation.",
            nz_legal_relevance=(
                "Useful comparison point for accuracy-sensitive drafting, but "
                "likely slower for interactive legal research."
            ),
            tasks=("legislation-summarisation", "drafting-quality", "policy-qa"),
            external_dependencies=("DiffusionGemma weights", "sampling profiler"),
        ),
        ArchitectureCandidate(
            id="gemma-diffusion",
            name="GemmaDiffusion",
            family="diffusion-language-model",
            source="community DiffusionGemma fine-tuning lineage",
            innovation="Community fine-tuning path for diffusion language models.",
            nz_legal_relevance=(
                "Potential route for clause summarisation experiments if "
                "DiffusionGemma weights and trainers are available."
            ),
            tasks=("legislation-summarisation", "drafting-quality"),
            external_dependencies=("GemmaDiffusion implementation", "model weights"),
        ),
        ArchitectureCandidate(
            id="nex-n2",
            name="Nex-N2",
            family="frontier-open-llm",
            source="nex-agi",
            innovation="Frontier open-source language model candidate.",
            nz_legal_relevance=(
                "Zero-shot comparator for cross-lingual legal concept transfer "
                "before any NZ-specific fine-tuning."
            ),
            tasks=("policy-qa", "legislation-summarisation", "drafting-quality"),
            external_dependencies=("Nex-N2 weights", "zero-shot benchmark shard"),
        ),
        ArchitectureCandidate(
            id="nex-rl",
            name="NexRL",
            family="post-training",
            source="nex-agi",
            innovation="Ultra-loosely-coupled reinforcement learning post-training.",
            nz_legal_relevance=(
                "Possible post-training path for legal-feedback alignment once "
                "supervised NZ adapters exist."
            ),
            tasks=("drafting-quality", "policy-qa"),
            status="monitor",
            external_dependencies=("NexRL toolkit", "legal feedback data"),
        ),
        ArchitectureCandidate(
            id="nex-au",
            name="NexAU",
            family="agent-framework",
            source="nex-agi",
            innovation="Tool-using agent framework for model orchestration.",
            nz_legal_relevance=(
                "Candidate orchestration layer for legal document workflows, not a "
                "backbone replacement by itself."
            ),
            tasks=("tool-use", "policy-qa"),
            status="monitor",
            external_dependencies=("NexAU framework", "tool benchmark harness"),
        ),
        ArchitectureCandidate(
            id="cosmos-3",
            name="NVIDIA Cosmos 3",
            family="world-foundation-model",
            source="NVIDIA",
            innovation="World foundation model for causal and multimodal reasoning.",
            nz_legal_relevance=(
                "Speculative comparator for causal-chain reasoning over legal events "
                "and policy consequences."
            ),
            tasks=("causal-reasoning", "policy-qa"),
            status="monitor",
            external_dependencies=("Cosmos access", "multimodal benchmark data"),
        ),
        ArchitectureCandidate(
            id="hy-world-2",
            name="Tencent HY-World 2.0",
            family="world-foundation-model",
            source="Tencent",
            innovation="Large world model for cross-modal sequence understanding.",
            nz_legal_relevance=(
                "Speculative comparator for mixed legal text, tables, and process "
                "diagrams if public access becomes available."
            ),
            tasks=("multimodal-legal", "policy-qa"),
            status="monitor",
            external_dependencies=("HY-World access", "multimodal benchmark data"),
        ),
        ArchitectureCandidate(
            id="mimo-v2-5",
            name="MiMo-V2.5",
            family="mixture-of-modalities",
            source="MiMo research lineage",
            innovation="Text, table, and structured-data mixture modelling.",
            nz_legal_relevance=(
                "Strong fit for schedules, tables, and structured clauses in "
                "legislation and committee reports."
            ),
            tasks=("multimodal-legal", "entity-linking", "policy-qa"),
            external_dependencies=("MiMo weights", "table benchmark shard"),
        ),
        ArchitectureCandidate(
            id="minimax-01",
            name="MiniMax-01",
            family="long-context-moe",
            source="MiniMax",
            innovation="Extreme long-context mixture-of-experts model.",
            nz_legal_relevance=(
                "Comparator for omnibus-bill and full-corpus reasoning when very "
                "long contexts are required."
            ),
            tasks=("long-context-retrieval", "policy-qa", "legislation-summarisation"),
            external_dependencies=("MiniMax access", "256K context benchmark"),
        ),
        ArchitectureCandidate(
            id="ring",
            name="Ring Attention",
            family="distributed-context",
            source="community ring-attention implementations",
            innovation="Distributed attention over partitioned long contexts.",
            nz_legal_relevance=(
                "Candidate infrastructure pattern for distributed full-Act and "
                "corpus-scale context windows."
            ),
            tasks=("long-context-retrieval", "policy-qa"),
            status="monitor",
            external_dependencies=("distributed runtime", "ring-attention implementation"),
        ),
        ArchitectureCandidate(
            id="ling",
            name="Ling",
            family="lightweight-architecture",
            source="community lightweight-model implementations",
            innovation="Lightweight architecture for efficient local deployment.",
            nz_legal_relevance=(
                "Candidate for edge or desktop legal NLP where model size and latency "
                "matter more than frontier reasoning."
            ),
            tasks=("nz-legal-citation", "entity-linking"),
            status="monitor",
            external_dependencies=("public implementation", "edge benchmark host"),
        ),
        ArchitectureCandidate(
            id="tirex",
            name="TiRex",
            family="tiled-recursive",
            source="community tiled-recursive implementations",
            innovation="Hierarchical tiled recursion for long documents.",
            nz_legal_relevance=(
                "Natural fit for hierarchical statutes, parts, schedules, and "
                "cross-referenced amendments."
            ),
            tasks=("long-context-retrieval", "nz-legal-citation", "policy-qa"),
            status="monitor",
            external_dependencies=("public implementation", "hierarchical benchmark"),
        ),
    ]
    return {candidate.id: candidate for candidate in candidates}


def _dominates(left: ArchitectureMetrics, right: ArchitectureMetrics) -> bool:
    maximize_left = (
        left.tokens_per_second,
        left.citation_f1,
        left.max_context_tokens,
        left.maori_token_integrity,
    )
    maximize_right = (
        right.tokens_per_second,
        right.citation_f1,
        right.max_context_tokens,
        right.maori_token_integrity,
    )
    minimize_left = (left.peak_memory_gb, left.perplexity)
    minimize_right = (right.peak_memory_gb, right.perplexity)

    no_worse = all(a >= b for a, b in zip(maximize_left, maximize_right, strict=True))
    no_worse = no_worse and all(
        a <= b for a, b in zip(minimize_left, minimize_right, strict=True)
    )
    strictly_better = any(
        a > b for a, b in zip(maximize_left, maximize_right, strict=True)
    ) or any(a < b for a, b in zip(minimize_left, minimize_right, strict=True))
    return no_worse and strictly_better


def pareto_frontier(
    evaluations: Iterable[ArchitectureEvaluation],
) -> list[ArchitectureEvaluation]:
    """Return evaluations not dominated on throughput, quality, context, and cost."""
    items = list(evaluations)
    return [
        candidate
        for candidate in items
        if not any(
            _dominates(other.metrics, candidate.metrics)
            for other in items
            if other is not candidate
        )
    ]


def _normalise(value: float, values: list[float], *, higher_is_better: bool) -> float:
    low = min(values)
    high = max(values)
    if high == low:
        return 1.0
    score = (value - low) / (high - low)
    return score if higher_is_better else 1.0 - score


def score_architecture(
    evaluation: ArchitectureEvaluation,
    population: Iterable[ArchitectureEvaluation],
) -> float:
    """Score a candidate for the NZ legal throughput-accuracy frontier."""
    items = list(population)
    metrics = evaluation.metrics
    metric_rows = [item.metrics for item in items]
    score = (
        0.35
        * _normalise(
            metrics.tokens_per_second,
            [row.tokens_per_second for row in metric_rows],
            higher_is_better=True,
        )
        + 0.25
        * _normalise(
            metrics.citation_f1,
            [row.citation_f1 for row in metric_rows],
            higher_is_better=True,
        )
        + 0.10
        * _normalise(
            metrics.perplexity,
            [row.perplexity for row in metric_rows],
            higher_is_better=False,
        )
        + 0.10
        * _normalise(
            metrics.peak_memory_gb,
            [row.peak_memory_gb for row in metric_rows],
            higher_is_better=False,
        )
        + 0.15
        * _normalise(
            metrics.max_context_tokens,
            [row.max_context_tokens for row in metric_rows],
            higher_is_better=True,
        )
        + 0.05
        * _normalise(
            metrics.maori_token_integrity,
            [row.maori_token_integrity for row in metric_rows],
            higher_is_better=True,
        )
    )
    return round(score, 6)


def rank_architectures(
    evaluations: Iterable[ArchitectureEvaluation],
) -> list[ArchitectureEvaluation]:
    """Rank candidates by weighted NZ legal suitability."""
    items = list(evaluations)
    return sorted(items, key=lambda item: score_architecture(item, items), reverse=True)


def recommend_architecture(
    evaluations: Iterable[ArchitectureEvaluation],
    *,
    min_citation_f1: float = 0.90,
    min_maori_token_integrity: float = 0.95,
) -> ArchitectureEvaluation:
    """Return the best candidate meeting minimum legal-quality gates."""
    eligible = [
        item
        for item in evaluations
        if item.metrics.citation_f1 >= min_citation_f1
        and item.metrics.maori_token_integrity >= min_maori_token_integrity
    ]
    if not eligible:
        raise ValueError("No architecture meets the configured NZ legal quality gates")
    return rank_architectures(eligible)[0]


def render_architecture_report(
    registry: dict[str, ArchitectureCandidate],
    evaluations: Iterable[ArchitectureEvaluation],
) -> str:
    """Render the Track 21 architecture comparison as Markdown."""
    items = list(evaluations)
    frontier = {item.architecture_id for item in pareto_frontier(items)}
    ranked = rank_architectures(items) if items else []
    try:
        recommendation = recommend_architecture(items) if items else None
    except ValueError:
        recommendation = None

    lines = [
        "# Bleeding-Edge Architecture Comparison",
        "",
        "This report is generated from the repo-side evaluation harness. "
        "External training and checkpoint publication remain gated on model "
        "downloads, GPU runs, and remote registry credentials.",
        "",
        "## Candidate Registry",
        "",
        "| ID | Family | NZ legal rationale | Tasks |",
        "| --- | --- | --- | --- |",
    ]
    for candidate in registry.values():
        lines.append(
            "| "
            f"{candidate.id} | {candidate.family} | "
            f"{candidate.nz_legal_relevance} | {', '.join(candidate.tasks)} |"
        )

    lines.extend(
        [
            "",
            "## Benchmark Results",
            "",
            "| Rank | ID | Benchmark | tok/s | GB | Citation F1 | PPL | "
            "Context | Maori integrity | Pareto |",
            "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    scores = {item.architecture_id: score_architecture(item, items) for item in items}
    for rank, item in enumerate(ranked, start=1):
        metrics = item.metrics
        lines.append(
            "| "
            f"{rank} | {item.architecture_id} | {item.benchmark_name} | "
            f"{metrics.tokens_per_second:.0f} | {metrics.peak_memory_gb:.1f} | "
            f"{metrics.citation_f1:.3f} | {metrics.perplexity:.2f} | "
            f"{metrics.max_context_tokens} | {metrics.maori_token_integrity:.3f} | "
            f"{'yes' if item.architecture_id in frontier else 'no'} |"
        )

    lines.extend(["", "## Recommendation", ""])
    if recommendation is None:
        lines.append(
            "No measured candidate is available. Retain the transformer baseline "
            "until at least three architectures complete the NZ legal benchmark."
        )
    else:
        candidate = registry[recommendation.architecture_id]
        lines.append(
            f"Select `{candidate.id}` ({candidate.name}) as the current "
            "throughput-accuracy frontier candidate for replacing the transformer "
            f"backbone. Weighted score: {scores[candidate.id]:.3f}."
        )

    lines.extend(
        [
            "",
            "## Next Gates",
            "",
            "- Run external model setup scripts in an environment with sufficient "
            "disk and GPU capacity.",
            "- Persist raw benchmark JSONL and profiler traces before accepting "
            "any checkpoint.",
            "- Re-run this report from measured outputs before changing the "
            "production backbone.",
        ]
    )
    return "\n".join(lines) + "\n"


def example_evaluations() -> list[ArchitectureEvaluation]:
    """Small deterministic example set for contract tests and dry-run reports."""
    return [
        ArchitectureEvaluation(
            "mor",
            "nz-legal-dev",
            ArchitectureMetrics(1400, 24, 0.91, 11.0, 32768, 0.98),
        ),
        ArchitectureEvaluation(
            "ttt-linear",
            "nz-legal-dev",
            ArchitectureMetrics(900, 30, 0.88, 14.5, 16384, 0.95),
        ),
        ArchitectureEvaluation(
            "mamba-3",
            "nz-legal-dev",
            ArchitectureMetrics(2200, 18, 0.90, 11.8, 65536, 0.97),
        ),
        ArchitectureEvaluation(
            "diffusion-gemma",
            "nz-legal-dev",
            ArchitectureMetrics(650, 20, 0.93, 10.7, 8192, 0.99),
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    """Run the deterministic architecture-evaluation report CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-registry", action="store_true")
    parser.add_argument("--example-report", action="store_true")
    parser.add_argument(
        "--architecture",
        choices=sorted(default_architecture_registry()),
    )
    args = parser.parse_args(argv)

    registry = default_architecture_registry()
    if args.print_registry:
        payload = {key: asdict(value) for key, value in registry.items()}
        print(json.dumps(payload, indent=2))  # noqa: T201
        return 0

    if args.example_report:
        evaluations = example_evaluations()
        if args.architecture:
            evaluations = [
                item for item in evaluations if item.architecture_id == args.architecture
            ]
        print(render_architecture_report(registry, evaluations))  # noqa: T201
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
