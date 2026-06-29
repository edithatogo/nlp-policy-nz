#!/usr/bin/env python
"""Benchmark sentence chunking vs Hugging Face ``tokenizers`` token-based chunking."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nlp_policy_nz.syntactic.chunking import chunk_by_sentence


def _build_corpus(record_count: int, repeat_factor: int) -> list[str]:
    base = (
        "The statute applies to all public-sector entities for the delivery of services "
        "to affected communities. This paragraph includes references, dates, and numbers "
        "so tokenizer behavior remains stable across benchmark runs."
    )
    return [f"{base} ({index}) " + (" " + base) * repeat_factor for index in range(record_count)]


def _chunk_count_by_token_target(token_count: int, target_tokens: int) -> int:
    return max(1, -(-token_count // target_tokens))


def _build_nlp() -> object:
    """Build a minimal spaCy pipeline for baseline sentence chunking."""
    try:
        import spacy
    except ImportError as exc:
        raise RuntimeError("spacy is not installed") from exc

    nlp = spacy.blank("en")  # type: ignore[attr-defined]
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")  # type: ignore[attr-defined]
    return nlp


def _bench_spacy(corpus: list[str], chunk_target_tokens: int) -> tuple[float, int]:
    nlp = _build_nlp()
    starts = time.perf_counter()
    chunk_count = 0
    for text in corpus:
        chunks = chunk_by_sentence(text, nlp)
        chunk_count += len(chunks)
    elapsed = time.perf_counter() - starts
    token_count = sum(len(text.split()) for text in corpus)
    return elapsed, max(chunk_count, _chunk_count_by_token_target(token_count, chunk_target_tokens))


def _bench_tokenizers(
    corpus: list[str],
    tokenizer: object,
    chunk_target_tokens: int,
) -> tuple[float, int]:
    starts = time.perf_counter()
    chunk_count = 0
    for text in corpus:
        ids = tokenizer.encode(text).ids  # type: ignore[attr-defined]
        chunk_count += _chunk_count_by_token_target(len(ids), chunk_target_tokens)
    return time.perf_counter() - starts, chunk_count


def _percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    index = max(0, round(0.95 * (len(values_sorted) - 1)))
    return values_sorted[index]


def _run_bench(
    fn: Callable[[list[str], int], tuple[float, int]],
    corpus: list[str],
    iterations: int,
    chunk_target: int,
) -> dict[str, Any]:
    timings: list[float] = []
    chunks = 0
    for _ in range(iterations):
        elapsed, chunk_count = fn(corpus, chunk_target)
        timings.append(elapsed)
        chunks = chunk_count

    total = sum(timings)
    avg = total / iterations
    throughput_chars_per_sec = sum(len(text) for text in corpus) * iterations / total
    return {
        "status": "measured",
        "iterations": iterations,
        "duration_seconds": round(total, 6),
        "avg_ms": round(avg * 1000, 6),
        "p95_ms": round(_percentile_95(timings) * 1000, 6),
        "chunks": chunks,
        "chunk_target_tokens": chunk_target,
        "throughput_chars_per_sec": round(throughput_chars_per_sec, 6),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=int, default=120)
    parser.add_argument("--repeat", type=int, default=24)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--chunk-size", type=int, default=256)
    parser.add_argument(
        "--evidence",
        default=Path(".tmp/track14_tokenizers_chunking_benchmark.json"),
        type=Path,
        help="Where to write benchmark evidence JSON.",
    )
    return parser


def _build_tokenizer(corpus: list[str]) -> object:
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers

    tokenizer = Tokenizer(models.BPE(unk_token="[UNK]"))  # noqa: S106
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    trainer = trainers.BpeTrainer(vocab_size=4_096, min_frequency=1, special_tokens=["[UNK]"])
    tokenizer.train_from_iterator(corpus, trainer=trainer)
    return tokenizer


def main(argv: list[str] | None = None) -> int:
    """Run the chunking benchmark and write evidence."""
    args = _build_parser().parse_args(argv)
    args.evidence.parent.mkdir(parents=True, exist_ok=True)

    corpus = _build_corpus(max(1, args.records), max(1, args.repeat))
    evidence: dict[str, Any] = {
        "track": "rust_backed_tooling_hotpaths_20260614",
        "experiment": "tokenizers_chunking",
        "corpus_size_chars": sum(len(text) for text in corpus),
        "records": len(corpus),
        "iterations": args.iterations,
        "chunk_target_tokens": args.chunk_size,
        "results": {},
    }

    if importlib.util.find_spec("tokenizers") is None:
        tokenizers_result = {
            "name": "tokenizers",
            "status": "missing_dependency",
            "error": "tokenizers is not installed",
            "iterations": args.iterations,
        }
    else:
        try:
            tokenizer = _build_tokenizer(corpus)
            tokenizers_result = _run_bench(
                lambda corpus_texts, target: _bench_tokenizers(corpus_texts, tokenizer, target),
                corpus,
                max(1, args.iterations),
                args.chunk_size,
            )
            tokenizers_result["name"] = "tokenizers"
        except Exception as exc:  # pragma: no cover - optional dependency path
            tokenizers_result = {
                "name": "tokenizers",
                "status": "missing_dependency",
                "error": str(exc),
                "iterations": args.iterations,
            }

    if importlib.util.find_spec("spacy") is None:
        spacy_result = {
            "name": "spacy_sentencizer",
            "status": "missing_dependency",
            "iterations": max(1, args.iterations),
            "error": "spacy is not installed",
        }
    else:
        try:
            spacy_result = _run_bench(
                _bench_spacy,
                corpus,
                max(1, args.iterations),
                args.chunk_size,
            )
            spacy_result["name"] = "spacy_sentencizer"
        except Exception as exc:  # pragma: no cover - optional dependency path
            spacy_result = {
                "name": "spacy_sentencizer",
                "status": "missing_dependency",
                "iterations": max(1, args.iterations),
                "error": str(exc),
            }

    evidence["results"] = {"tokenizers": tokenizers_result, "spacy_sentence": spacy_result}
    args.evidence.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"wrote evidence to {args.evidence}")  # noqa: T201
    print(f"tokenizers: {tokenizers_result['status']}")  # noqa: T201
    if spacy_result["status"] == "measured":
        print(f"spacy_sentence avg_ms={spacy_result['avg_ms']:.3f}")  # noqa: T201
    else:
        print(f"spacy_sentence: {spacy_result['status']}")  # noqa: T201
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
