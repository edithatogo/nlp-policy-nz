"""Check that the declared package version stays aligned across files."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8-sig")


def _pyproject_version() -> str:
    return str(tomllib.loads(_text("pyproject.toml"))["project"]["version"])


def _quoted_assignment(path: str, name: str) -> str:
    match = re.search(
        rf'^{re.escape(name)}\s*=\s*"([^"]+)"\s*$', _text(path), re.MULTILINE
    )
    if not match:
        raise ValueError(f"{path} does not define {name}")
    return match.group(1)


def check_version_consistency() -> list[str]:
    """Return any version consistency errors found in the repository."""
    failures: list[str] = []

    package_version = _pyproject_version()
    init_version = _quoted_assignment("src/nlp_policy_nz/__init__.py", "__version__")
    if package_version != init_version:
        failures.append(
            "Version mismatch: pyproject.toml "
            f"{package_version} != __init__.py {init_version}"
        )
    if not SEMVER_RE.fullmatch(package_version):
        failures.append(f"Version is not SemVer-like: {package_version}")

    return failures


def main() -> int:
    """Run the version consistency check and print any failures."""
    failures = check_version_consistency()
    if failures:
        for _f in failures:
            pass
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
