"""Generate all Track 35 publication artifacts.

Usage:
    python scripts/generate_all_artifacts.py --output-dir artifacts
"""

# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nlp_policy_nz.analysis import write_analysis_artifacts  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        "-o",
        default=ROOT / "artifacts",
        type=Path,
        help="Directory for generated artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    """Generate Track 35 artifacts and print the written paths."""
    args = _parse_args()
    written = write_analysis_artifacts(args.output_dir, repo_root_path=ROOT)
    for path in sorted(written.values()):
        sys.stdout.write(f"{path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
