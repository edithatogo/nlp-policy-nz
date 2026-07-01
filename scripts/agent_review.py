"""Render a structured PR review from quality-gate results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nlp_policy_nz.automation.agentic import (  # noqa: E402
    build_review_summary,
    render_review_markdown,
)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checks-json", help="Path to JSON gate results.")
    parser.add_argument("--markdown", action="store_true", help="Print markdown summary.")
    return parser.parse_args()


def main() -> int:
    """Render the agent review report."""
    args = parse_args()
    payload = json.loads(Path(args.checks_json).read_text(encoding="utf-8")) if args.checks_json else {}
    summary = build_review_summary(payload)
    output = render_review_markdown(summary) if args.markdown else json.dumps(summary, indent=2)
    sys.stdout.write(output + ("\n" if not output.endswith("\n") else ""))
    return 0 if summary["decision"] == "approve" else 1


if __name__ == "__main__":
    raise SystemExit(main())
