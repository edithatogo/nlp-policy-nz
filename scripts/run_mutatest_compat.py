"""Run the pinned mutatest CLI with Python 3.11+ set-sampling compatibility."""

from __future__ import annotations

import random
from collections.abc import Iterable

_sample = random.sample


def _compatible_sample(population: Iterable[object], k: int, *, counts=None):
    """Convert mutatest's set population before Python rejects it."""
    if isinstance(population, (set, frozenset)):
        population = tuple(population)
    if counts is None:
        return _sample(population, k)
    return _sample(population, k, counts=counts)


random.sample = _compatible_sample  # type: ignore[assignment]

from mutatest.cli import cli_main  # noqa: E402

raise SystemExit(cli_main())
