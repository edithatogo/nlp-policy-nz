"""Advance completed Conductor tracks when all plan tasks are done."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nlp_policy_nz.automation.agentic import advance_completed_track  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track-id", required=True)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Advance a completed Conductor track and print the result."""
    args = parse_args()
    result = advance_completed_track(Path(args.root), args.track_id)
    output = json.dumps(result, indent=2) if args.json else str(result)
    sys.stdout.write(output + ("\n" if not output.endswith("\n") else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
