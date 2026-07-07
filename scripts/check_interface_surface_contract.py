"""CI wrapper for the Track 85 cross-surface contract check."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nlp_policy_nz.governance.interface_contract import main


if __name__ == "__main__":
    raise SystemExit(main())
