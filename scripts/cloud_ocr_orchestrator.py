"""Metadata-only CLI used by the Track 91 GitHub Actions workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Keep direct script execution equivalent to the installed CLI. GitHub Actions
# invokes this file from a checkout before installing the project editable.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nlp_policy_nz.extraction.hathi_ingestion import HathiArchiveItem  # noqa: E402
from nlp_policy_nz.ocr.cloud_ops import (  # noqa: E402
    BudgetLimits,
    CloudRunPlan,
    LedgerState,
    build_cloud_run_plan,
    quarantine_failed,
    retry_failed,
    transition_row,
    write_signed_run_report,
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
    if len(raw_items) > args.volume_limit:
        raise ValueError("metadata manifest exceeds the configured volume limit")
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


def _apply_worker_results(plan: CloudRunPlan, path: Path) -> CloudRunPlan:
    payload = _read_json(path)
    results = payload.get("results", payload) if isinstance(payload, dict) else payload
    if not isinstance(results, list):
        raise ValueError("worker result manifest must contain a results list")
    result = plan
    for entry in results:
        if not isinstance(entry, dict):
            raise ValueError("worker result entries must be objects")
        item_id = entry.get("item_id")
        state = entry.get("state")
        if not isinstance(item_id, str) or not isinstance(state, str):
            raise ValueError("worker results require item_id and state")
        result = transition_row(
            result,
            item_id,
            LedgerState(state),
            error_code=entry.get("error_code"),
            output_digest=entry.get("output_digest"),
        )
    return result


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
    parser.add_argument("--results", type=Path)
    parser.add_argument("--signing-key-env", default="CLOUD_OCR_SIGNING_KEY")
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
    if args.command == "collect" and args.results is None:
        parser.error("collect requires a worker result manifest as --results")
    if args.command == "collect":
        try:
            plan = _apply_worker_results(plan, args.results)  # type: ignore[arg-type]
        except (KeyError, TypeError, ValueError) as error:
            parser.error(str(error))
    if args.command == "retry":
        plan = retry_failed(plan)  # type: ignore[arg-type]
    elif args.command == "quarantine":
        plan = quarantine_failed(plan)  # type: ignore[arg-type]
    elif args.command == "publish" and plan is not None:
        if plan.quarantined_item_ids or any(row.state.value != "published" for row in plan.ledger):
            parser.error("publication requires every ledger row to be published and unquarantined")
        signing_key = os.environ.get(args.signing_key_env)
        if not signing_key:
            parser.error(f"publication requires {args.signing_key_env}")
        write_signed_run_report(plan, args.output, signing_key=signing_key)
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
