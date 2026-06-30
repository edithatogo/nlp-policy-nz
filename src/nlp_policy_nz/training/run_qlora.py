"""CLI stub for Track 20 QLoRA job specification generation."""

from __future__ import annotations

import argparse
import json
import sys

from nlp_policy_nz.training.trainers import create_qlora_job


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse QLoRA job arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", required=True)
    parser.add_argument(
        "--task", required=True, choices=["citation", "deontic", "entity", "qa", "maori"]
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--hub-model-id", required=True)
    parser.add_argument(
        "--print-spec",
        action="store_true",
        help="Print the serializable job spec and exit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Create a QLoRA job spec.

    Full GPU training is intentionally not launched by this lightweight stub;
    it creates the auditable job contract consumed by Track 20 scripts.
    """
    args = _parse_args(argv)
    job = create_qlora_job(
        model_name=args.model_name,
        task=args.task,
        output_dir=args.output_dir,
        hub_model_id=args.hub_model_id,
    )
    if args.print_spec:
        sys.stdout.write(f"{json.dumps(job.to_dict(), indent=2)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
