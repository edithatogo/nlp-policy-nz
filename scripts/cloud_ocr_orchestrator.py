"""Metadata-only CLI used by the Track 91 GitHub Actions workflow."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from nlp_policy_nz.extraction.hathi_ingestion import HathiArchiveItem
from nlp_policy_nz.ocr.cloud_ops import (
    BudgetLimits,
    CloudRunPlan,
    build_cloud_run_plan,
    quarantine_failed,
    retry_failed,
)


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_plan(path: Path | None) -> CloudRunPlan | None:
    if path is None or not path.is_file():
        return None
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return None
    candidate = payload.get("plan", payload)
    if not isinstance(candidate, dict) or "ledger" not in candidate:
        return None
    return CloudRunPlan.model_validate(candidate)


def _build_plan(args: argparse.Namespace) -> CloudRunPlan:
    if args.input is None:
        raise ValueError("validate requires a metadata-only item manifest")
    payload = _read_json(args.input)
    raw_items = payload.get("items", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_items, list):
        raise ValueError("metadata manifest must contain an items list")
    items = tuple(HathiArchiveItem.model_validate(item) for item in raw_items)
    return build_cloud_run_plan(
        items,
        run_id=args.run_id,
        pipeline_version=args.pipeline_version,
        budget=BudgetLimits(
            max_cost_usd=args.max_cost_usd,
            max_concurrency=args.max_concurrency,
            max_retries=args.max_retries,
        ),
        shard_size=args.shard_size,
    )


def _write_artifact(
    *,
    args: argparse.Namespace,
    status: str,
    plan: CloudRunPlan | None = None,
    **extra: object,
) -> None:
    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "command": args.command,
        "volume_limit": args.volume_limit,
        "shard_size": args.shard_size,
        "max_cost_usd": args.max_cost_usd,
        "payload_policy": "metadata_only",
        "status": status,
    }
    if plan is not None:
        payload["plan"] = plan.model_dump(mode="json")
    payload.update(extra)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main() -> int:
    """Validate or pass metadata-only cloud operation artifacts downstream."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("validate", "plan", "collect", "retry", "quarantine", "publish", "pilot", "sbom"),
    )
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--volume-limit", type=int, default=3)
    parser.add_argument("--shard-size", type=int, default=100)
    parser.add_argument("--max-cost-usd", type=float, default=25.0)
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", "local-run"))
    parser.add_argument("--pipeline-version", default="1.0.0")
    args = parser.parse_args()
    if args.volume_limit < 1 or args.volume_limit > 3:
        parser.error("volume limit must be between 1 and 3")
    if args.shard_size < 1 or args.max_cost_usd < 0 or args.max_concurrency < 1 or args.max_retries < 0:
        parser.error("shard size and budget/concurrency/retry limits must be valid positive values")
    plan = _load_plan(args.input)
    if args.command == "validate" and args.input is not None:
        plan = _build_plan(args)
    if args.command in {"plan", "collect", "retry", "quarantine", "publish"} and plan is None:
        parser.error(f"{args.command} requires a CloudRunPlan artifact as --input")
    if args.command == "retry":
        plan = retry_failed(plan)  # type: ignore[arg-type]
    elif args.command == "quarantine":
        plan = quarantine_failed(plan)  # type: ignore[arg-type]
    elif args.command == "publish" and plan is not None:
        blocked = [row.item_id for row in plan.ledger if row.state.value in {"pending", "failed"}]
        blocked.extend(plan.quarantined_item_ids)
        if blocked:
            parser.error("publication blocked until all ledger rows are complete and unquarantined")
    if args.command == "collect" and plan is not None:
        _write_artifact(
            args=args,
            status="external_gate_required",
            plan=plan,
            required_prerequisites=["cloud worker checkpoint", "worker result manifest"],
        )
        return 0
    if args.command == "pilot":
        _write_artifact(
            args=args,
            status="external_gate_required",
            required_prerequisites=[
                "configured GitHub OIDC trust",
                "pinned cloud OCR worker",
                "Hugging Face staging repository",
                "signed checkpoint report",
            ],
        )
        return 0
    if args.command == "sbom":
        _write_artifact(args=args, status="generated", bomFormat="CycloneDX", specVersion="1.5", components=[])
        return 0
    _write_artifact(args=args, status="planned" if args.command in {"validate", "plan"} else "reconciled", plan=plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
