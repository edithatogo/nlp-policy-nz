"""Create and publish a code-release deposition to Zenodo.

The workflow uses this script for tag-triggered releases.  It deliberately
publishes the repository source archive and citation metadata, not a guessed
legislation dataset.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def _request(url: str, token: str, *, method: str = "GET", data: bytes | None = None) -> dict:
    request = Request(url, data=data, method=method)  # noqa: S310
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/json")
    try:
        with urlopen(request, timeout=60) as response:  # noqa: S310
            payload = response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Zenodo API {error.code} for {url}: {detail}") from error
    return json.loads(payload) if payload else {}


def _archive(root: Path, version: str, output: Path) -> None:
    prefix = f"nlp-policy-nz-{version}/"
    with tarfile.open(output, "w:gz") as archive:
        result = subprocess.run(
            ["git", "archive", "--format=tar", f"--prefix={prefix}", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        import io

        with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as source:
            for member in source:
                extracted = source.extractfile(member) if member.isfile() else None
                archive.addfile(member, extracted)


def main() -> int:
    """Create and optionally publish the tagged source archive."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=Path(".tmp/zenodo-release"))
    parser.add_argument("--environment", choices=("production", "sandbox"), default="production")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"nlp-policy-nz-{args.version}.tar.gz"
    _archive(root, args.version, archive)
    metadata = json.loads((root / ".zenodo.json").read_text(encoding="utf-8"))
    metadata.update(
        {
            "version": args.version,
            "publication_date": __import__("datetime").date.today().isoformat(),
            "upload_type": "software",
            "resource_type": "software",
        }
    )
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.dry_run:
        sys.stdout.write(f"{archive}\n")
        return 0

    token_name = "ZENODO_TOKEN" if args.environment == "production" else "ZENODO_SANDBOX_TOKEN"
    token = os.environ.get(token_name)
    if not token:
        raise SystemExit(f"{token_name} is required for publication")
    base = "https://zenodo.org/api" if args.environment == "production" else "https://sandbox.zenodo.org/api"
    deposition = _request(f"{base}/deposit/depositions", token, method="POST", data=json.dumps({"metadata": metadata}).encode())
    deposition_id = deposition["id"]
    upload_url = deposition["links"]["bucket"]
    request = Request(  # noqa: S310
        f"{upload_url}/{archive.name}", data=archive.read_bytes(), method="PUT"
    )
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Content-Type", "application/octet-stream")
    request.add_header("Content-Length", str(archive.stat().st_size))
    with urlopen(request, timeout=120):  # noqa: S310
        pass
    _request(f"{base}/deposit/depositions/{deposition_id}/actions/publish", token, method="POST")
    sys.stdout.write(f"{deposition.get('doi') or deposition_id}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
