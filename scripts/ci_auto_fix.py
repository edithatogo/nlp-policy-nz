"""Run repo auto-fix commands for CI healing workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nlp_policy_nz.automation.agentic import run_auto_fix  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--report", help="Write a JSON report to this path.")
    return parser.parse_args()


def main() -> int:
    """Run the auto-fix routine and optionally write a report."""
    args = parse_args()
    result = run_auto_fix(Path(args.root))
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if result["basedpyright_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
