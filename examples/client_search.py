"""Run a semantic search query against the API."""

from __future__ import annotations

import json
import os
import sys

from nlp_policy_nz.client import NLPPolicyNZClient


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    query = args[0] if args else "climate change"
    base_url = os.getenv("NLP_POLICY_NZ_API_URL", "http://127.0.0.1:8000")
    with NLPPolicyNZClient(base_url=base_url) as client:
        result = client.search(query=query, top_k=3)
    print(json.dumps(result.model_dump(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
