"""Prepare a Google Jules dispatch payload for GPU-gated tasks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--gpu", default="1")
    parser.add_argument("--project", default="nlp-policy-nz")
    parser.add_argument("--output", help="Optional file to write the dispatch payload.")
    return parser.parse_args()


def main() -> int:
    """Render a Jules dispatch payload."""
    args = parse_args()
    payload = {
        "task": args.task,
        "gpu": args.gpu,
        "project": args.project,
        "mode": "dry-run",
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
