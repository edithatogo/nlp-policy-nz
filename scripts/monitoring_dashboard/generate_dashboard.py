"""Generate a static HTML data-quality dashboard from persisted reports."""

from __future__ import annotations

import argparse
from pathlib import Path

from nlp_policy_nz.quality import history_reports, write_dashboard_html


def build_parser() -> argparse.ArgumentParser:
    """Build the dashboard generator parser."""
    parser = argparse.ArgumentParser(
        prog="generate_dashboard",
        description="Render a static HTML dashboard for persisted quality reports.",
    )
    parser.add_argument(
        "--history-dir",
        type=str,
        default="data/quality/runs",
        help="Directory containing quality report JSON files.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/quality/dashboard.html",
        help="Destination HTML dashboard file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Render the dashboard and write it to disk."""
    args = build_parser().parse_args(argv)
    reports = history_reports(args.history_dir)
    output = write_dashboard_html(reports, Path(args.output))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
