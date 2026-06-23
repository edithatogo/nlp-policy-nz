"""Run a Memray allocation trace over the nlp-policy-nz processing CLI."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    """Build command-line arguments for the Memray runner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "-i", required=True, help="Input file or directory.")
    parser.add_argument("--output", "-o", required=True, help="Output Parquet path.")
    parser.add_argument(
        "--source",
        "-s",
        choices=["legislation", "hansard"],
        default="hansard",
        help="Corpus source to pass to the pipeline CLI.",
    )
    parser.add_argument(
        "--trace",
        default="docs/profiling/memray.bin",
        help="Destination Memray binary trace.",
    )
    parser.add_argument(
        "--flamegraph",
        default="docs/profiling/memray-flamegraph.html",
        help="Destination Memray flamegraph report.",
    )
    parser.add_argument(
        "--evidence",
        default="docs/profiling/memray-evidence.json",
        help="Destination JSON evidence note for the allocation trace.",
    )
    parser.add_argument(
        "--with-embeddings",
        action="store_true",
        help="Generate embeddings during the profiled run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run Memray and generate a flamegraph report."""
    args = _build_parser().parse_args(argv)
    if shutil.which("memray") is None:
        sys.stderr.write("memray is not installed. Install Track 19 dev dependencies first.\n")
        return 2

    trace = Path(args.trace)
    flamegraph = Path(args.flamegraph)
    trace.parent.mkdir(parents=True, exist_ok=True)
    flamegraph.parent.mkdir(parents=True, exist_ok=True)
    pipeline_command = [
        "memray",
        "run",
        "--force",
        "--output",
        str(trace),
        "-m",
        "nlp_policy_nz.cli.main",
        "process",
        "--input",
        args.input,
        "--output",
        args.output,
        "--source",
        args.source,
    ]
    if not args.with_embeddings:
        pipeline_command.append("--no-embeddings")

    rc = subprocess.call(pipeline_command)
    flamegraph_command = ["memray", "flamegraph", "--output", str(flamegraph), str(trace)]
    flamegraph_rc = None
    if rc == 0:
        flamegraph_rc = subprocess.call(flamegraph_command)

    evidence = Path(args.evidence)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "tool": "memray",
        "created_at": datetime.now(UTC).isoformat(),
        "command": pipeline_command,
        "return_code": rc,
        "flamegraph_command": flamegraph_command,
        "flamegraph_return_code": flamegraph_rc,
        "input": str(Path(args.input)),
        "input_exists": Path(args.input).exists(),
        "output": str(Path(args.output)),
        "trace": str(trace),
        "trace_exists": trace.exists(),
        "flamegraph": str(flamegraph),
        "flamegraph_exists": flamegraph.exists(),
        "source": args.source,
        "with_embeddings": args.with_embeddings,
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "corpus_claim": "caller supplied input; no full-corpus claim is implied by this wrapper",
    }
    evidence.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return rc if rc != 0 else int(flamegraph_rc or 0)


if __name__ == "__main__":
    raise SystemExit(main())
