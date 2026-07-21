"""Validate the candidate NZ FOI-O conformance packet without promotion."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_DIMENSIONS = {"positive", "negative", "temporal", "non-equivalence"}


def validate(packet: dict[str, Any], root: Path) -> list[str]:
    """Return violations in the NZ conformance packet and pinned fixture."""
    errors: list[str] = []
    if packet.get("schema_version") != "foio-nz-conformance-packet-v1":
        errors.append("schema_version is invalid")
    if packet.get("candidate_only") is not True or packet.get("promotion") != "no-promotion":
        errors.append("packet must remain candidate-only and no-promotion")
    if packet.get("status") != "pending-independent-review":
        errors.append("packet must remain pending-independent-review")
    if set(packet.get("required_dimensions", [])) != REQUIRED_DIMENSIONS:
        errors.append("required_dimensions must cover all four fixture dimensions")
    blockers = packet.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        errors.append("blockers must explain the external gates")
    rac = packet.get("rac_conformance")
    if not isinstance(rac, dict) or rac.get("status") != "candidate-contract-only":
        errors.append("RAC reference must remain candidate-contract-only")
    fixture = packet.get("fixture")
    if not isinstance(fixture, dict):
        errors.append("fixture reference is required")
    else:
        fixture_path = root / fixture.get("path", "")
        if not fixture_path.is_file():
            errors.append("fixture path does not exist")
        else:
            digest = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            if digest != fixture.get("sha256"):
                errors.append("fixture SHA-256 does not match")
    return errors


def main() -> int:
    """Run packet validation from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=Path("data/foio/nz_conformance_packet.json"))
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.stdout.write(json.dumps({"passed": False, "errors": [str(exc)]}) + "\n")
        return 1
    errors = validate(packet, Path.cwd()) if isinstance(packet, dict) else ["packet must be a JSON object"]
    sys.stdout.write(json.dumps({"passed": not errors, "promotion": "no-promotion", "errors": errors}, indent=2) + "\n")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
