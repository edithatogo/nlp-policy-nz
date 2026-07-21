"""Validate the Track 92 cross-repository collection inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA = "track92-source-inventory-v1"
REQUIRED_GATES = {"rights", "source_pin", "independent_review", "legal_review", "profile_owner_approval"}


def validate(inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if inventory.get("schema_version") != SCHEMA:
        errors.append(f"schema_version must be {SCHEMA}")
    if inventory.get("candidate_only") is not True:
        errors.append("candidate_only must be true")
    repositories = inventory.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        errors.append("at least one source repository is required")
    else:
        for index, item in enumerate(repositories):
            if not isinstance(item, dict):
                errors.append(f"repositories[{index}] must be an object")
                continue
            for key in ("repository", "role"):
                if not isinstance(item.get(key), str) or not item[key]:
                    errors.append(f"repositories[{index}].{key} is required")
    promotion = inventory.get("promotion")
    if not isinstance(promotion, dict):
        errors.append("promotion object is required")
    else:
        if promotion.get("decision") != "no-promotion":
            errors.append("empty or incomplete inventory must remain no-promotion")
        blockers = promotion.get("blockers")
        if not isinstance(blockers, list) or not blockers or not all(isinstance(item, str) and item for item in blockers):
            errors.append("promotion.blockers must explain every unresolved gate")
        gates = promotion.get("required_gates")
        if not isinstance(gates, list) or set(gates) != REQUIRED_GATES:
            errors.append("promotion.required_gates must declare every human and provenance gate")
        if promotion.get("completed_gates") != [] and not promotion.get("evidence_packages"):
            errors.append("completed gates require evidence packages")
    if inventory.get("jurisdictions") != []:
        errors.append("jurisdiction entries require pinned source and review evidence before registration")
    if inventory.get("evidence_packages") != []:
        errors.append("evidence packages require the full external intake contract before registration")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=Path("data/track92/source_inventory.json"))
    args = parser.parse_args()
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, sort_keys=True))
        return 1
    errors = validate(inventory) if isinstance(inventory, dict) else ["inventory must be a JSON object"]
    report = {"schema_version": SCHEMA, "passed": not errors, "decision": "no-promotion", "errors": errors}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
