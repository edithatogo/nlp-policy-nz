"""Prometheus-style metrics helpers for the API server."""

from __future__ import annotations

from collections import Counter, defaultdict
from threading import Lock
from typing import Any

_LOCK = Lock()
_REQUEST_COUNTS: Counter[tuple[str, str, int, str]] = Counter()
_REQUEST_DURATION_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
_REQUEST_HISTOGRAM: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0] * (len(_REQUEST_DURATION_BUCKETS) + 1))
_REQUEST_DURATION_SUM: Counter[tuple[str, str]] = Counter()
_REQUEST_DURATION_COUNT: Counter[tuple[str, str]] = Counter()
_ERROR_COUNTS: Counter[tuple[int, str, str]] = Counter()
_ACTIVE_REQUESTS = 0
_MODEL_LOADED = 0


def reset_metrics() -> None:
    """Reset all metrics for test isolation."""
    global _ACTIVE_REQUESTS, _MODEL_LOADED
    with _LOCK:
        _REQUEST_COUNTS.clear()
        _REQUEST_HISTOGRAM.clear()
        _REQUEST_DURATION_SUM.clear()
        _REQUEST_DURATION_COUNT.clear()
        _ERROR_COUNTS.clear()
        _ACTIVE_REQUESTS = 0
        _MODEL_LOADED = 0


def set_model_loaded(loaded: bool) -> None:
    """Set the model-load gauge."""
    global _MODEL_LOADED
    with _LOCK:
        _MODEL_LOADED = int(bool(loaded))


def increment_active_requests() -> None:
    """Increment the active request gauge."""
    global _ACTIVE_REQUESTS
    with _LOCK:
        _ACTIVE_REQUESTS += 1


def decrement_active_requests() -> None:
    """Decrement the active request gauge."""
    global _ACTIVE_REQUESTS
    with _LOCK:
        _ACTIVE_REQUESTS = max(0, _ACTIVE_REQUESTS - 1)


def record_request(
    *,
    method: str,
    endpoint: str,
    status: int,
    scope: str,
    duration_seconds: float,
) -> None:
    """Record a completed request."""
    key = (method.upper(), endpoint, status, scope or "public")
    bucket_key = (method.upper(), endpoint)
    with _LOCK:
        _REQUEST_COUNTS[key] += 1
        _REQUEST_DURATION_SUM[bucket_key] += duration_seconds
        _REQUEST_DURATION_COUNT[bucket_key] += 1
        buckets = _REQUEST_HISTOGRAM[bucket_key]
        placed = False
        for idx, bound in enumerate(_REQUEST_DURATION_BUCKETS):
            if duration_seconds <= bound:
                buckets[idx] += 1
                placed = True
                break
        if not placed:
            buckets[-1] += 1
        if status >= 400:
            _ERROR_COUNTS[(status, endpoint, scope or "public")] += 1


def _render_labels(labels: dict[str, Any]) -> str:
    return ",".join(f'{key}="{value}"' for key, value in labels.items())


def render_metrics() -> str:
    """Render the in-memory metrics in Prometheus exposition format."""
    with _LOCK:
        lines: list[str] = []
        lines.extend(
            [
                "# HELP nlp_policy_nz_requests_total Total completed API requests.",
                "# TYPE nlp_policy_nz_requests_total counter",
            ]
        )
        for (method, endpoint, status, scope), count in sorted(_REQUEST_COUNTS.items()):
            lines.append(
                f'nlp_policy_nz_requests_total{{method="{method}",endpoint="{endpoint}",status="{status}",scope="{scope}"}} {count}'
            )
        lines.extend(
            [
                "# HELP nlp_policy_nz_request_duration_seconds Request duration histogram.",
                "# TYPE nlp_policy_nz_request_duration_seconds histogram",
            ]
        )
        for (method, endpoint), buckets in sorted(_REQUEST_HISTOGRAM.items()):
            cumulative = 0
            for idx, bound in enumerate(_REQUEST_DURATION_BUCKETS):
                cumulative += buckets[idx]
                lines.append(
                    f'nlp_policy_nz_request_duration_seconds_bucket{{method="{method}",endpoint="{endpoint}",le="{bound}"}} {cumulative}'
                )
            cumulative += buckets[-1]
            lines.append(
                f'nlp_policy_nz_request_duration_seconds_bucket{{method="{method}",endpoint="{endpoint}",le="+Inf"}} {cumulative}'
            )
            total = _REQUEST_DURATION_COUNT[(method, endpoint)]
            lines.append(
                f'nlp_policy_nz_request_duration_seconds_sum{{method="{method}",endpoint="{endpoint}"}} {float(_REQUEST_DURATION_SUM[(method, endpoint)])}'
            )
            lines.append(
                f'nlp_policy_nz_request_duration_seconds_count{{method="{method}",endpoint="{endpoint}"}} {total}'
            )
        lines.extend(
            [
                "# HELP nlp_policy_nz_errors_total Total API errors by status code.",
                "# TYPE nlp_policy_nz_errors_total counter",
            ]
        )
        for (status, endpoint, scope), count in sorted(_ERROR_COUNTS.items()):
            lines.append(
                f'nlp_policy_nz_errors_total{{status="{status}",endpoint="{endpoint}",scope="{scope}"}} {count}'
            )
        lines.extend(
            [
                "# HELP nlp_policy_nz_active_requests Current active requests.",
                "# TYPE nlp_policy_nz_active_requests gauge",
                f"nlp_policy_nz_active_requests {_ACTIVE_REQUESTS}",
                "# HELP nlp_policy_nz_model_loaded Model load state.",
                "# TYPE nlp_policy_nz_model_loaded gauge",
                f"nlp_policy_nz_model_loaded {_MODEL_LOADED}",
            ]
        )
        return "\n".join(lines) + "\n"
