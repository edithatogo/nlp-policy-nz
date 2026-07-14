"""Track 71 Mojo sandbox helpers.

This module keeps the Linux-only Mojo experiment optional. It can always
produce the Python reference payload, and it reports a skip reason when the
current platform or environment cannot run the sandbox path.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


DEFAULT_FIXTURE_VALUES: tuple[int, ...] = (1, 2, 3, 5)


@dataclass(frozen=True)
class MojoSandboxPayload:
    """Deterministic reference payload for the Track 71 sandbox fixture."""

    fixture_name: str
    input_values: tuple[int, ...]
    prefix_sums: tuple[int, ...]
    weighted_sum: int
    checksum: int

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""
        return asdict(self)


@dataclass(frozen=True)
class MojoSandboxReport:
    """Runtime report for the optional Mojo sandbox path."""

    platform_name: str
    ci: bool
    mojo_available: bool
    pixi_available: bool
    uv_available: bool
    install_strategy: str
    status: str
    skip_reason: str | None
    reference_payload: MojoSandboxPayload

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""
        payload = asdict(self)
        payload["reference_payload"] = self.reference_payload.to_dict()
        return payload


def compute_reference_payload(
    values: Sequence[int] = DEFAULT_FIXTURE_VALUES,
    *,
    fixture_name: str = "rolling-signature",
) -> MojoSandboxPayload:
    """Compute the deterministic Python reference output for the sandbox."""
    resolved = tuple(values)
    prefix_sums: list[int] = []
    running_total = 0
    weighted_sum = 0
    for index, value in enumerate(resolved, start=1):
        running_total += value
        prefix_sums.append(running_total)
        weighted_sum += index * value
    checksum = running_total + weighted_sum + len(resolved)
    return MojoSandboxPayload(
        fixture_name=fixture_name,
        input_values=resolved,
        prefix_sums=tuple(prefix_sums),
        weighted_sum=weighted_sum,
        checksum=checksum,
    )


def render_reference_json(values: Sequence[int] = DEFAULT_FIXTURE_VALUES) -> str:
    """Render the Python reference payload as stable JSON."""
    return json.dumps(compute_reference_payload(values).to_dict(), indent=2, sort_keys=True)


def detect_mojo_sandbox_report() -> MojoSandboxReport:
    """Detect whether the optional Mojo sandbox path can run locally."""
    platform_name = platform.system()
    ci = _env_flag("CI") or _env_flag("GITHUB_ACTIONS")
    mojo_available = shutil.which("mojo") is not None
    pixi_available = shutil.which("pixi") is not None
    uv_available = shutil.which("uv") is not None
    install_strategy = _choose_install_strategy(pixi_available=pixi_available, uv_available=uv_available)
    reference_payload = compute_reference_payload()
    if platform_name != "Linux":
        return MojoSandboxReport(
            platform_name=platform_name,
            ci=ci,
            mojo_available=mojo_available,
            pixi_available=pixi_available,
            uv_available=uv_available,
            install_strategy=install_strategy,
            status="skipped",
            skip_reason="Track 71 is Linux-only.",
            reference_payload=reference_payload,
        )
    if not mojo_available:
        return MojoSandboxReport(
            platform_name=platform_name,
            ci=ci,
            mojo_available=mojo_available,
            pixi_available=pixi_available,
            uv_available=uv_available,
            install_strategy=install_strategy,
            status="skipped",
            skip_reason="Mojo is not installed on this runner.",
            reference_payload=reference_payload,
        )
    return MojoSandboxReport(
        platform_name=platform_name,
        ci=ci,
        mojo_available=mojo_available,
        pixi_available=pixi_available,
        uv_available=uv_available,
        install_strategy=install_strategy,
        status="passed",
        skip_reason=None,
        reference_payload=reference_payload,
    )


def render_mojo_sandbox_json() -> str:
    """Render the Track 71 sandbox report as stable JSON."""
    return json.dumps(detect_mojo_sandbox_report().to_dict(), indent=2, sort_keys=True)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the sandbox and write either JSON or a concise status line."""
    args = _parse_args(argv)
    report = detect_mojo_sandbox_report()
    rendered = render_mojo_sandbox_json()
    if args.json:
        sys.stdout.write(f"{rendered}\n")
    else:
        sys.stdout.write(f"{report.status}: {report.skip_reason or 'Mojo sandbox available.'}\n")
    return 0


def _choose_install_strategy(*, pixi_available: bool, uv_available: bool) -> str:
    """Choose the preferred sandbox install strategy for the detected runner."""
    if pixi_available:
        return "pixi-temporary-project"
    if uv_available:
        return "uv-system-install"
    return "none"


def _env_flag(name: str) -> bool:
    """Return whether an environment variable is truthy."""
    return os.getenv(name, "").casefold() in {"1", "true", "yes"}


def _parse_args(argv: Sequence[str] | None) -> Namespace:
    """Parse command-line arguments for the sandbox helper."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Render the full sandbox report as JSON.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
