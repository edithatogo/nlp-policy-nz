"""Build a reproducible Zenodo payload for pinned Cloud OCR pilot evidence.

The payload deliberately contains only the public, metadata-only Hugging Face
snapshot named by the OCR registry.  It must not be used to assert a completed
OCR benchmark or to package source images and OCR text that are not present in
that snapshot.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import tarfile
from pathlib import Path

DEFAULT_VERSION = "track131-repo-scaffold-v1"
DEFAULT_BENCHMARK_ID = "nz-historical-ocr-v1"
DEFAULT_REPO_ID = "edithatogo/nlp-policy-nz-cloud-ocr-pilots"
DEFAULT_REVISION = "0d588e59e9093919135a5feb9358aa690b43d408"
ARCHIVE_PREFIX = "nlp-policy-nz-cloud-ocr-pilot-evidence"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_files(source_dir: Path) -> list[Path]:
    """Return payload files in a stable order, excluding local Hub metadata."""
    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file() and ".cache" not in path.relative_to(source_dir).parts
    )


def _archive(source_dir: Path, files: list[Path], output: Path) -> None:
    """Write a byte-stable tar.gz containing the supplied source files."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with (
        output.open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed,
        tarfile.open(mode="w", fileobj=compressed, format=tarfile.PAX_FORMAT) as archive,
    ):
        for path in files:
            relative = path.relative_to(source_dir).as_posix()
            info = tarfile.TarInfo(f"{ARCHIVE_PREFIX}/{relative}")
            info.size = path.stat().st_size
            info.mode = 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            with path.open("rb") as handle:
                archive.addfile(info, handle)


def _metadata(version: str) -> dict[str, object]:
    return {
        "title": "NLP Policy NZ Cloud OCR Pilot Evidence (metadata-only)",
        "description": (
            "Versioned operational evidence for the NLP Policy NZ Cloud OCR pilot. "
            "This release contains public metadata-only run reports, reconciliation "
            "records, and provenance for one bounded Tesseract documentation example. "
            "It does not contain a general OCR corpus, source images, OCR text, or "
            "validated production benchmark results."
        ),
        "upload_type": "dataset",
        "version": version,
        "creators": [{"name": "Mordaunt, Dylan A", "orcid": "0000-0002-9775-0603"}],
        "keywords": [
            "optical-character-recognition",
            "ocr",
            "new-zealand",
            "provenance",
            "metadata-only",
        ],
        "related_identifiers": [
            {
                "identifier": "https://huggingface.co/datasets/edithatogo/nlp-policy-nz-cloud-ocr-pilots",
                "relation": "isDerivedFrom",
                "scheme": "url",
            },
            {
                "identifier": "https://github.com/edithatogo/nlp-policy-nz",
                "relation": "isSupplementTo",
                "scheme": "url",
            },
        ],
        "notes": (
            "Source snapshot is pinned to Hugging Face revision "
            f"{DEFAULT_REVISION}. The archive excludes local Hugging Face cache files."
        ),
    }


def build_payload(
    source_dir: Path,
    archive_path: Path,
    manifest_path: Path,
    metadata_path: Path,
    *,
    version: str = DEFAULT_VERSION,
) -> dict[str, object]:
    """Build the archive and its JSON manifest and metadata sidecars."""
    source_dir = source_dir.resolve()
    if not source_dir.is_dir():
        raise ValueError(f"source directory does not exist: {source_dir}")

    files = _source_files(source_dir)
    if not files:
        raise ValueError(f"source directory has no release files: {source_dir}")
    _archive(source_dir, files, archive_path)
    entries = [
        {
            "path": path.relative_to(source_dir).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in files
    ]
    manifest = {
        "schema_version": "nlp-policy-nz.ocr-release-payload.v1",
        "artifact_kind": "metadata-only-cloud-ocr-pilot-evidence",
        "artifact_version": version,
        "benchmark_id": DEFAULT_BENCHMARK_ID,
        "hf_source": {"repo_id": DEFAULT_REPO_ID, "revision": DEFAULT_REVISION},
        "archive": {
            "file_name": archive_path.name,
            "format": "tar.gz",
            "content_prefix": ARCHIVE_PREFIX,
            "bytes": archive_path.stat().st_size,
            "sha256": _sha256(archive_path),
        },
        "files": entries,
        "scope": {
            "payload_policy": "metadata_only",
            "contains_source_images": False,
            "contains_ocr_text": False,
            "contains_validated_benchmark_results": False,
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metadata_path.write_text(json.dumps(_metadata(version), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    """Build the payload from a fully downloaded, revision-pinned HF snapshot."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    args = parser.parse_args()
    manifest = build_payload(
        args.source_dir,
        args.archive,
        args.manifest,
        args.metadata,
        version=args.version,
    )
    sys.stdout.write(json.dumps(manifest["archive"], sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
