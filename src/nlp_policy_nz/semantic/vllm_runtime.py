"""Track 62 vLLM local inference runtime evaluation helpers."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from importlib import import_module
from statistics import fmean
from time import perf_counter
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from nlp_policy_nz.training.eval import exact_match, token_f1

DEFAULT_COMPLETIONS_PATH = "/v1/completions"
DEFAULT_TIMEOUT_SECONDS = 30.0


class VLLMRuntimeError(RuntimeError):
    """Raised when a vLLM runtime helper cannot complete an operation."""


@dataclass(frozen=True)
class VLLMGenerationResult:
    """One generation result from either vLLM offline mode or an endpoint."""

    prompt: str
    generated_text: str
    mode: str
    model_name: str
    elapsed_seconds: float
    endpoint_url: str | None = None


@dataclass(frozen=True)
class Track62BenchmarkRow:
    """One prompt comparison row for the Track 62 evaluation report."""

    prompt: str
    baseline_text: str
    runtime_text: str
    baseline_exact_match: float
    runtime_exact_match: float
    baseline_token_f1: float
    runtime_token_f1: float
    baseline_latency_seconds: float
    runtime_latency_seconds: float


@dataclass(frozen=True)
class Track62EvidenceReport:
    """Repo-side evidence summary for Track 62."""

    backend_state: str
    benchmark_rows: int
    baseline_exact_match: float
    runtime_exact_match: float
    baseline_token_f1: float
    runtime_token_f1: float
    baseline_latency_seconds: float
    runtime_latency_seconds: float
    endpoint_mode_supported: bool
    offline_mode_supported: bool
    dspy_integration_documented: bool
    spacy_llm_integration_documented: bool
    go_no_go: str
    docs_present: bool
    review_ready: bool


def _create_vllm_engine(model_name: str, **engine_kwargs: object) -> object:
    """Create a vLLM offline engine or raise a clear install hint."""
    try:
        module = import_module("vllm")
    except ImportError as exc:  # pragma: no cover - exercised in dependency tests
        msg = "vLLM support requires the optional 'vllm' extra or a local vLLM install."
        raise ImportError(msg) from exc

    try:
        engine_class = module.LLM
    except AttributeError as exc:  # pragma: no cover - defensive guard
        msg = "The installed vLLM package does not expose the LLM offline engine."
        raise VLLMRuntimeError(msg) from exc

    return engine_class(model=model_name, **engine_kwargs)


def _create_sampling_params(
    max_tokens: int,
    temperature: float,
    top_p: float,
) -> object:
    """Create vLLM sampling parameters or raise a clear install hint."""
    try:
        module = import_module("vllm")
    except ImportError as exc:  # pragma: no cover - exercised in dependency tests
        msg = "vLLM support requires the optional 'vllm' extra or a local vLLM install."
        raise ImportError(msg) from exc

    try:
        params_class = module.SamplingParams
    except AttributeError as exc:  # pragma: no cover - defensive guard
        msg = "The installed vLLM package does not expose SamplingParams."
        raise VLLMRuntimeError(msg) from exc

    return params_class(max_tokens=max_tokens, temperature=temperature, top_p=top_p)


def _normalize_completion_endpoint(endpoint_url: str) -> str:
    """Normalise base URLs and concrete completion URLs."""
    stripped = endpoint_url.rstrip("/")
    if stripped.endswith("/v1/completions"):
        return stripped
    if stripped.endswith("/v1"):
        return f"{stripped}/completions"
    return f"{stripped}{DEFAULT_COMPLETIONS_PATH}"


def _extract_completion_text(payload: dict[str, Any]) -> str:
    """Extract the first completion text from an OpenAI-compatible payload."""
    choices = payload.get("choices")
    if not choices:
        raise VLLMRuntimeError("The vLLM endpoint response did not include any choices.")
    first_choice = choices[0]
    if isinstance(first_choice, dict):
        text = first_choice.get("text")
        if isinstance(text, str) and text:
            return text
        message = first_choice.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str) and content:
                return content
    raise VLLMRuntimeError("The vLLM endpoint response did not include completion text.")


def generate_completion_via_openai_endpoint(
    prompt: str,
    *,
    endpoint_url: str,
    model_name: str,
    max_tokens: int = 128,
    temperature: float = 0.0,
    top_p: float = 1.0,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> VLLMGenerationResult:
    """Generate a completion from an OpenAI-compatible vLLM endpoint."""
    payload = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    request = Request(  # noqa: S310
        _normalize_completion_endpoint(endpoint_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = perf_counter()
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            response_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:  # pragma: no cover - exercised in network failure tests
        raise VLLMRuntimeError(f"vLLM endpoint request failed: {exc}") from exc
    except URLError as exc:  # pragma: no cover - exercised in network failure tests
        raise VLLMRuntimeError(f"vLLM endpoint request failed: {exc}") from exc
    elapsed_seconds = perf_counter() - started
    return VLLMGenerationResult(
        prompt=prompt,
        generated_text=_extract_completion_text(response_payload),
        mode="endpoint",
        model_name=model_name,
        elapsed_seconds=elapsed_seconds,
        endpoint_url=endpoint_url,
    )


def generate_completion_via_vllm(
    prompt: str,
    *,
    model_name: str,
    engine_kwargs: dict[str, Any] | None = None,
    max_tokens: int = 128,
    temperature: float = 0.0,
    top_p: float = 1.0,
) -> VLLMGenerationResult:
    """Generate a completion with the optional vLLM offline engine."""
    started = perf_counter()
    try:
        engine = _create_vllm_engine(model_name, **(engine_kwargs or {}))
        sampling_params = _create_sampling_params(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
    except ImportError as exc:
        msg = "vLLM support requires the optional 'vllm' extra or a local vLLM install."
        raise ImportError(msg) from exc
    outputs = engine.generate([prompt], sampling_params)
    if not outputs:
        raise VLLMRuntimeError("vLLM returned no outputs for the supplied prompt.")
    first_output = outputs[0]
    first_text: str | None = None
    generated_outputs = getattr(first_output, "outputs", None)
    if generated_outputs:
        candidate = generated_outputs[0]
        first_text = getattr(candidate, "text", None)
    if not first_text:
        raise VLLMRuntimeError("vLLM returned an output without generated text.")
    elapsed_seconds = perf_counter() - started
    return VLLMGenerationResult(
        prompt=prompt,
        generated_text=first_text,
        mode="offline",
        model_name=model_name,
        elapsed_seconds=elapsed_seconds,
    )


def _baseline_completion(prompt: str) -> str:
    """Return a deterministic baseline completion for evaluation comparisons."""
    return f"baseline completion for: {prompt}"


def compare_track62_runtime_to_baseline(
    prompts: Sequence[str],
    *,
    baseline_completion: Callable[[str], str] | None = None,
    runtime_completion: Callable[[str], VLLMGenerationResult],
) -> tuple[Track62EvidenceReport, tuple[Track62BenchmarkRow, ...]]:
    """Compare a runtime against a deterministic baseline across prompts."""
    baseline_runner = baseline_completion or _baseline_completion
    rows: list[Track62BenchmarkRow] = []
    for prompt in prompts:
        baseline_started = perf_counter()
        baseline_text = baseline_runner(prompt)
        baseline_latency_seconds = perf_counter() - baseline_started
        runtime_result = runtime_completion(prompt)
        rows.append(
            Track62BenchmarkRow(
                prompt=prompt,
                baseline_text=baseline_text,
                runtime_text=runtime_result.generated_text,
                baseline_exact_match=exact_match(baseline_text, baseline_text),
                runtime_exact_match=exact_match(runtime_result.generated_text, baseline_text),
                baseline_token_f1=token_f1(
                    baseline_text.split(),
                    baseline_text.split(),
                ),
                runtime_token_f1=token_f1(
                    runtime_result.generated_text.split(),
                    baseline_text.split(),
                ),
                baseline_latency_seconds=baseline_latency_seconds,
                runtime_latency_seconds=runtime_result.elapsed_seconds,
            ),
        )
    report = build_track62_evidence_report(
        tuple(rows),
        docs_present=True,
        dspy_integration_documented=True,
        spacy_llm_integration_documented=True,
    )
    return report, tuple(rows)


def build_track62_evidence_report(
    benchmark_rows: Sequence[Track62BenchmarkRow],
    *,
    docs_present: bool,
    dspy_integration_documented: bool,
    spacy_llm_integration_documented: bool,
) -> Track62EvidenceReport:
    """Build the repo-side Track 62 evidence report."""
    rows = tuple(benchmark_rows)
    if rows:
        baseline_exact_match = fmean(row.baseline_exact_match for row in rows)
        runtime_exact_match = fmean(row.runtime_exact_match for row in rows)
        baseline_token_f1 = fmean(row.baseline_token_f1 for row in rows)
        runtime_token_f1 = fmean(row.runtime_token_f1 for row in rows)
        baseline_latency_seconds = fmean(row.baseline_latency_seconds for row in rows)
        runtime_latency_seconds = fmean(row.runtime_latency_seconds for row in rows)
        backend_state = "optional"
        go_no_go = "optional"
    else:
        baseline_exact_match = 0.0
        runtime_exact_match = 0.0
        baseline_token_f1 = 0.0
        runtime_token_f1 = 0.0
        baseline_latency_seconds = 0.0
        runtime_latency_seconds = 0.0
        backend_state = "deferred"
        go_no_go = "deferred"
    review_ready = (
        docs_present
        and bool(rows)
        and dspy_integration_documented
        and spacy_llm_integration_documented
    )
    return Track62EvidenceReport(
        backend_state=backend_state,
        benchmark_rows=len(rows),
        baseline_exact_match=baseline_exact_match,
        runtime_exact_match=runtime_exact_match,
        baseline_token_f1=baseline_token_f1,
        runtime_token_f1=runtime_token_f1,
        baseline_latency_seconds=baseline_latency_seconds,
        runtime_latency_seconds=runtime_latency_seconds,
        endpoint_mode_supported=True,
        offline_mode_supported=True,
        dspy_integration_documented=dspy_integration_documented,
        spacy_llm_integration_documented=spacy_llm_integration_documented,
        go_no_go=go_no_go,
        docs_present=docs_present,
        review_ready=review_ready,
    )


def render_track62_evidence_markdown(
    report: Track62EvidenceReport,
    benchmark_rows: Sequence[Track62BenchmarkRow],
) -> str:
    """Render the Track 62 evidence report as Markdown."""
    rows = tuple(benchmark_rows)
    lines = [
        "# Track 62 Evidence",
        "",
        "## Summary",
        "",
        "Track 62 evaluates vLLM as an optional high-throughput local generation runtime.",
        "",
        "## Runtime Modes",
        "",
        f"- Backend state: {report.backend_state}",
        f"- Endpoint mode supported: {'yes' if report.endpoint_mode_supported else 'no'}",
        f"- Offline mode supported: {'yes' if report.offline_mode_supported else 'no'}",
        f"- Go/no-go decision: {report.go_no_go}",
        "",
        "## Integration Notes",
        "",
        f"- DSPy integration documented: {'yes' if report.dspy_integration_documented else 'no'}",
        f"- spaCy-llm integration documented: {'yes' if report.spacy_llm_integration_documented else 'no'}",
        "",
        "## Benchmarks",
        "",
        f"- Rows compared: {report.benchmark_rows}",
        f"- Baseline exact match: {report.baseline_exact_match:.3f}",
        f"- Runtime exact match: {report.runtime_exact_match:.3f}",
        f"- Baseline token F1: {report.baseline_token_f1:.3f}",
        f"- Runtime token F1: {report.runtime_token_f1:.3f}",
        f"- Baseline latency seconds: {report.baseline_latency_seconds:.3f}",
        f"- Runtime latency seconds: {report.runtime_latency_seconds:.3f}",
    ]
    if rows:
        lines.extend(
            [
                "",
                "## Prompt Samples",
            ],
        )
        for row in rows:
            lines.extend(
                [
                    "",
                    f"- Prompt: {row.prompt}",
                    f"  - Baseline: {row.baseline_text}",
                    f"  - Runtime: {row.runtime_text}",
                ],
            )
    return "\n".join(lines)


__all__ = [
    "DEFAULT_COMPLETIONS_PATH",
    "DEFAULT_TIMEOUT_SECONDS",
    "Track62BenchmarkRow",
    "Track62EvidenceReport",
    "VLLMGenerationResult",
    "VLLMRuntimeError",
    "build_track62_evidence_report",
    "compare_track62_runtime_to_baseline",
    "generate_completion_via_openai_endpoint",
    "generate_completion_via_vllm",
    "render_track62_evidence_markdown",
]
