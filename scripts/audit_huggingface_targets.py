"""Validate Hugging Face audit evidence locally; optional live endpoint probes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "registry" / "huggingface_audit.json"
DOC_PATH = ROOT / "docs" / "registry-readiness.md"
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")


def _normalize_status(value: str) -> str:
    return value.replace("-", "_").lower()


def check_audit_json() -> list[str]:
    """Return offline Hugging Face audit JSON violations."""
    errors: list[str] = []
    if not AUDIT_PATH.exists():
        errors.append(f"missing {AUDIT_PATH}")
        return errors

    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    status = str(audit.get("status", ""))
    if DOC_PATH.exists():
        doc_text = DOC_PATH.read_text(encoding="utf-8")
        if _normalize_status(status) not in _normalize_status(doc_text):
            errors.append("huggingface_audit.json status does not match registry-readiness.md")

    status_lower = status.lower()
    if ("doi_pending" in status_lower or "doi-pending" in status_lower) and not audit.get("blockers"):
        errors.append("huggingface_audit.json blockers must be non-empty while doi pending")

    for index, target in enumerate(audit.get("targets", []), start=1):
        revision = str(target.get("revision", ""))
        if not REVISION_RE.fullmatch(revision):
            errors.append(f"huggingface target {index} revision must be a 40-char git sha")
        if not target.get("croissant_verified"):
            errors.append(f"huggingface target {index} croissant_verified must be true")

    return errors


def probe_targets() -> list[str]:
    """Probe live Croissant endpoints recorded in the audit JSON."""
    errors: list[str] = []
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    for target in audit.get("targets", []):
        endpoint = target.get("croissant_endpoint")
        if not endpoint:
            errors.append(f"missing croissant_endpoint for {target.get('repo_id')}")
            continue
        parsed = urlparse(endpoint)
        if parsed.scheme != "https":
            errors.append(f"croissant endpoint must use https for {target.get('repo_id')}")
            continue
        request = Request(endpoint, headers={"User-Agent": "nlp-policy-nz-registry-audit/1.0"})  # noqa: S310
        try:
            with urlopen(request, timeout=20) as response:  # noqa: S310
                if response.status != 200:
                    errors.append(f"croissant probe failed for {target.get('repo_id')}: HTTP {response.status}")
        except URLError as exc:
            errors.append(f"croissant probe failed for {target.get('repo_id')}: {exc}")
    return errors


def main() -> int:
    """Run offline audit validation and optional network probes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--network",
        action="store_true",
        help="Probe live Hugging Face Croissant endpoints (default: offline JSON validation only)",
    )
    args = parser.parse_args()

    problems = check_audit_json()
    if args.network:
        problems.extend(probe_targets())

    if problems:
        sys.stdout.write("\n".join(problems) + "\n")
        return 1

    mode = "offline+network" if args.network else "offline"
    sys.stdout.write(f"huggingface audit ({mode}): OK\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
