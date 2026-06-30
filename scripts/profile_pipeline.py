"""Run a Scalene profile over the nlp-policy-nz processing CLI."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from contextlib import suppress
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


def _write_launcher_script(path: Path, command_args: list[str]) -> Path:
    """Write a temporary launcher that invokes the repo CLI."""
    path.mkdir(parents=True, exist_ok=True)
    launcher = path / "track19_scalene_launcher.py"
    payload = ", ".join(json.dumps(arg) for arg in command_args)
    repo_root = Path(__file__).resolve().parents[1]
    launcher.write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "import sys",
                f"ROOT = Path({json.dumps(str(repo_root))})",
                'SRC = ROOT / "src"',
                "if str(ROOT) not in sys.path:",
                "    sys.path.insert(0, str(ROOT))",
                "if str(SRC) not in sys.path:",
                "    sys.path.insert(0, str(SRC))",
                "from nlp_policy_nz.cli.main import main",
                f"raise SystemExit(main([{payload}]))",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return launcher


def main(argv: list[str] | None = None) -> int:
    """Run Scalene against the package CLI and return its exit code."""
    args = _build_parser().parse_args(argv)
    if shutil.which("scalene") is None:
        sys.stderr.write("scalene is not installed. Install Track 19 dev dependencies first.\n")
        return 2

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    profile_json = report.parent / "scalene-profile.json"
    launcher = _write_launcher_script(
        Path(args.output).parent,
        [
            "process",
            "--input",
            args.input,
            "--output",
            args.output,
            "--source",
            args.source,
        ]
        + (["--no-embeddings"] if not args.with_embeddings else []),
    )
    command = ["scalene", "run", "-o", str(profile_json), str(launcher)]
    if not args.with_embeddings:
        pass

    html_command = ["scalene", "view", "--html", str(profile_json)]

    rc = subprocess.call(command)
    html_rc = None
    if rc == 0:
        html_rc = subprocess.call(html_command, cwd=report.parent)
        generated = report.parent / "scalene-profile.html"
        if html_rc == 0 and generated.exists() and generated != report:
            generated.replace(report)

    evidence = Path(args.evidence)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "tool": "scalene",
        "created_at": datetime.now(UTC).isoformat(),
        "command": command,
        "html_command": html_command,
        "return_code": rc,
        "html_return_code": html_rc,
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
    with suppress(FileNotFoundError):
        launcher.unlink()
    with suppress(FileNotFoundError):
        profile_json.unlink()
    return rc if rc != 0 else int(html_rc or 0)


if __name__ == "__main__":
    raise SystemExit(main())
