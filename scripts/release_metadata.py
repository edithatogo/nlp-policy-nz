#!/usr/bin/env python3
"""Generate release metadata files for Track 45 automation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nlp_policy_nz.release_engineering import generate_release_assets


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for release metadata generation."""
    parser = argparse.ArgumentParser(description="Generate VERSION.json and CITATION.cff.")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--output-dir", default=Path.cwd(), type=Path)
    parser.add_argument("--version", default=None)
    parser.add_argument("--dataset-revision", default="0")
    parser.add_argument("--title", default="nlp-policy-nz")
    parser.add_argument("--repository-url", default="https://github.com/edithatogo/nlp-policy-nz")
    parser.add_argument("--doi", default=None)
    parser.add_argument("--zenodo-description", default="Versioned nlp-policy-nz software release.")
    parser.add_argument("--zenodo-version-doi", default=None)
    parser.add_argument("--zenodo-concept-doi", default=None)
    parser.add_argument("--zenodo-record-url", default=None)
    parser.add_argument("--zenodo-verified", action="store_true")
    parser.add_argument("--release-notes", default="")
    parser.add_argument("--commit-sha", default=None)
    parser.add_argument("--since-ref", default=None)
    parser.add_argument(
        "--author",
        action="append",
        dest="authors",
        default=None,
        help="Repeatable author name for CITATION.cff",
    )
    return parser.parse_args()


def main() -> None:
    """Generate the release metadata files and report their locations."""
    args = parse_args()
    authors = args.authors or ["Maintainer"]
    result = generate_release_assets(
        args.root,
        args.output_dir,
        version=args.version,
        dataset_revision=args.dataset_revision,
        title=args.title,
        authors=authors,
        repository_url=args.repository_url,
        release_notes=args.release_notes,
        doi=args.doi,
        zenodo_description=args.zenodo_description,
        zenodo_version_doi=args.zenodo_version_doi,
        zenodo_concept_doi=args.zenodo_concept_doi,
        zenodo_record_url=args.zenodo_record_url,
        zenodo_verified=args.zenodo_verified,
        since_ref=args.since_ref,
        commit_sha=args.commit_sha,
    )
    manifest = result["manifest"]
    sys.stdout.write(f"{manifest['version']}\n")
    sys.stdout.write(f"{result['version_path']}\n")
    sys.stdout.write(f"{result['citation_path']}\n")
    sys.stdout.write(f"{result['changelog_path']}\n")
    sys.stdout.write(f"{result['zenodo_path']}\n")
    sys.stdout.write(f"{result['mirror_manifest_path']}\n")


if __name__ == "__main__":
    main()
