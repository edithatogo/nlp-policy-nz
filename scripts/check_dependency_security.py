"""Enforce the repository's dependency vulnerability policy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nlp_policy_nz.security.dependency_security import (  # noqa: E402
    HIGH_SEVERITY_THRESHOLD,
    audit_dependency_report,
    collect_high_severity_findings,
    run_dependency_audit,
)


def main(argv: list[str] | None = None) -> int:
    """Run pip-audit and fail only for critical/high vulnerabilities."""
    _ = argv
    report = run_dependency_audit(ROOT)
    findings = collect_high_severity_findings(report, threshold=HIGH_SEVERITY_THRESHOLD)
    actionable_findings = [finding for finding in findings if finding.fix_versions]
    if findings:
        for finding in findings:
            fix_versions = ", ".join(finding.fix_versions) or "unfixed"
            sys.stderr.write(
                f"{finding.package} {finding.version} {finding.vuln_id} "
                f"{finding.severity_label} fix: {fix_versions}\n",
            )
        if actionable_findings:
            return 1
        sys.stderr.write("Only high-severity findings without published fixes were reported.\n")
        return 0

    if audit_dependency_report(report):
        sys.stderr.write("Dependency audit completed with only below-threshold findings.\n")
    else:
        sys.stderr.write("Dependency audit found no known vulnerabilities.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
