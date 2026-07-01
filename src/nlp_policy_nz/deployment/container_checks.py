"""Lightweight container smoke checks for external service reachability."""

from __future__ import annotations

import socket
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlparse

import requests


@dataclass(frozen=True, slots=True)
class SmokeCheckResult:
    """Result for one container reachability probe."""

    name: str
    target: str
    reachable: bool


def probe_http_endpoint(url: str, timeout: float = 5.0) -> bool:
    """Return ``True`` when an HTTP endpoint responds successfully."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return True


def probe_tcp_endpoint(host: str, port: int, timeout: float = 5.0) -> bool:
    """Return ``True`` when a TCP endpoint accepts a socket connection."""
    with socket.create_connection((host, port), timeout=timeout):
        return True


def _probe_target(target: str, timeout: float) -> bool:
    parsed = urlparse(target)
    if parsed.scheme == "tcp":
        if not parsed.hostname or parsed.port is None:
            msg = f"Invalid TCP target: {target!r}"
            raise ValueError(msg)
        return probe_tcp_endpoint(parsed.hostname, parsed.port, timeout=timeout)
    return probe_http_endpoint(target, timeout=timeout)


def run_container_smoke_checks(
    targets: Mapping[str, str],
    *,
    timeout: float = 5.0,
) -> list[SmokeCheckResult]:
    """Probe named service targets and return their reachability status."""
    results: list[SmokeCheckResult] = []
    for name, target in targets.items():
        try:
            reachable = _probe_target(target, timeout)
        except (OSError, requests.RequestException, ValueError):
            reachable = False
        results.append(SmokeCheckResult(name=name, target=target, reachable=reachable))
    return results
