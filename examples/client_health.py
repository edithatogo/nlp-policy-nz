"""Print API health and version details."""

from __future__ import annotations

import json
import os

from nlp_policy_nz.client import NLPPolicyNZClient


def main() -> int:
    base_url = os.getenv("NLP_POLICY_NZ_API_URL", "http://127.0.0.1:8000")
    with NLPPolicyNZClient(base_url=base_url) as client:
        payload = {
            "health": client.health().model_dump(),
            "version": client.version().model_dump(),
        }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
