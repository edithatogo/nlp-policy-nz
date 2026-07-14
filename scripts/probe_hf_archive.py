"""Probe a public Hugging Face archive endpoint without credentials."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from nlp_policy_nz.publication.hf_archive import (
    CONFIG_NAMES,
    probe_huggingface_endpoint,
    write_endpoint_probe,
)


def main() -> int:
    """Run and persist a public metadata and Dataset Viewer probe."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--configs", nargs="+", default=CONFIG_NAMES)
    args = parser.parse_args()
    report = probe_huggingface_endpoint(args.dataset_id, configs=tuple(args.configs))
    write_endpoint_probe(report, args.output)
    sys.stdout.write(json.dumps(report.model_dump(mode="json"), sort_keys=True) + "\n")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
