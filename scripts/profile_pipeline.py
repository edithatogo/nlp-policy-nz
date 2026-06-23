"""Run a Scalene profile over the nlp-policy-nz processing CLI."""

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
    """Build command-line arguments for the Scalene runner."""
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
        "--report",
        default="docs/profiling/scalene.html",
        help="Destination Scalene HTML report.",
    )
    parser.add_argument(
        "--evidence",
        default="docs/profiling/profile-pipeline-evidence.json",
        help="Destination JSON evidence note for the profiling run.",
    )
    parser.add_argument(
        "--with-embeddings",
        action="store_true",
        help="Generate embeddings during the profiled run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run Scalene against the package CLI and return its exit code."""
    args = _build_parser().parse_args(argv)
    if shutil.which("scalene") is None:
        sys.stderr.write("scalene is not installed. Install Track 19 dev dependencies first.\n")
        return 2

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "scalene",
        "--reduced-profile",
        "--html",
        "--outfile",
        str(report),
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
        command.append("--no-embeddings")

    rc = subprocess.call(command)
    evidence = Path(args.evidence)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "tool": "scalene",
        "created_at": datetime.now(UTC).isoformat(),
        "command": command,
        "return_code": rc,
        "input": str(Path(args.input)),
        "input_exists": Path(args.input).exists(),
        "output": str(Path(args.output)),
        "report": str(report),
        "report_exists": report.exists(),
        "source": args.source,
        "with_embeddings": args.with_embeddings,
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "corpus_claim": "caller supplied input; no full-corpus claim is implied by this wrapper",
    }
    evidence.write_text(f"{json.dumps(payload, indent=2)}\n", encoding="utf-8")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
