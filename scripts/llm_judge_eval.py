"""Deterministic LLM-as-judge evaluation harness for legal NLP outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nlp_policy_nz.automation.agentic import evaluate_judge_run  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="JSON file with evaluation cases.")
    parser.add_argument("--example", action="store_true", help="Run an example evaluation.")
    return parser.parse_args()


def main() -> int:
    """Evaluate candidate outputs and print a JSON report."""
    args = parse_args()
    if args.example:
        payload = [
            {
                "model_id": "baseline",
                "prompt": "Summarise the clause.",
                "prediction": "The clause grants powers.",
                "reference": "The clause grants powers.",
            },
            {
                "model_id": "candidate",
                "prompt": "Summarise the clause.",
                "prediction": "It is about something else.",
                "reference": "The clause grants powers.",
            },
        ]
    else:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8")) if args.input else []
    result = evaluate_judge_run(payload)
    sys.stdout.write(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
