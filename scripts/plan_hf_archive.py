"""Materialize or publish a Track 90 Hugging Face archive bundle."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from nlp_policy_nz.archive.schema import ArchiveBundle
from nlp_policy_nz.publication.hf_archive import (
    build_publication_plan,
    probe_huggingface_endpoint,
    publish_hf_archive,
    write_endpoint_probe,
)


def main() -> int:
    """Validate, materialize, or publish a structured archive bundle."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--collection-id", required=True)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--verify-endpoint", action="store_true")
    args = parser.parse_args()
    bundle = ArchiveBundle.model_validate_json(args.bundle.read_text(encoding="utf-8"))
    plan = build_publication_plan(
        bundle, dataset_id=args.dataset_id, collection_id=args.collection_id
    )
    endpoint_reports: list[object] = []

    def endpoint_probe(dataset_id: str) -> bool:
        report = probe_huggingface_endpoint(dataset_id, configs=plan.config_names)
        endpoint_reports.append(report)
        return report.passed

    url = publish_hf_archive(
        bundle,
        plan,
        args.output_dir,
        token=os.environ.get("HF_TOKEN"),
        dry_run=not args.publish,
        endpoint_probe=endpoint_probe if args.verify_endpoint else None,
    )
    if endpoint_reports:
        write_endpoint_probe(endpoint_reports[0], args.output_dir / "endpoint-probe.json")
    sys.stdout.write(f"{url}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
