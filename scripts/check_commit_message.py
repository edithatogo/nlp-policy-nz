"""Validate commit messages with the repository's conventional commit policy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main(argv: list[str] | None = None) -> int:
    """Lint a commit-msg file or the current CI commit range."""
    from nlp_policy_nz.governance.commit_message import (
        lint_commit_message,
        lint_commit_messages,
        load_commit_messages_from_git,
    )

    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        if len(args) != 1:
            sys.stderr.write("Usage: check_commit_message.py [commit-msg-file]\n")
            return 2
        message = Path(args[0]).read_text(encoding="utf-8")
        errors = lint_commit_message(message)
    else:
        errors = lint_commit_messages(load_commit_messages_from_git())

    if errors:
        for error in errors:
            sys.stderr.write(f"{error}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
