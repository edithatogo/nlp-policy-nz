"""Release engineering helpers for semantic versioning and publication metadata."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

SEMVER_RE = re.compile(r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$")
COMMIT_RE = re.compile(r"^(?P<type>[a-z]+)(?P<breaking>!)?(?:\([^)]+\))?:", re.IGNORECASE)


def _normalise_timestamp(build_timestamp: str | None) -> str:
    if build_timestamp is not None:
        return build_timestamp
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_semver(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version)
    if match is None:
        raise ValueError(f"Invalid semantic version: {version}")
    return int(match.group("major")), int(match.group("minor")), int(match.group("patch"))


def detect_bump_level(commit_messages: Sequence[str]) -> str:
    """Return the semantic version bump required by conventional commits."""
    if not commit_messages:
        return "none"

    bump = "none"
    for message in commit_messages:
        text = message.strip()
        if not text:
            continue
        if "BREAKING CHANGE:" in text or "BREAKING-CHANGE:" in text:
            return "major"
        subject = text.splitlines()[0]
        match = COMMIT_RE.match(subject)
        if match is None:
            if bump == "none":
                bump = "patch"
            continue
        commit_type = match.group("type").lower()
        if match.group("breaking"):
            return "major"
        if commit_type == "feat":
            bump = "minor" if bump in {"none", "patch"} else bump
        elif commit_type == "fix":
            bump = "patch" if bump == "none" else bump
        elif bump == "none":
            bump = "patch"
    return bump


def bump_version(version: str, level: str) -> str:
    """Return the next semantic version for the requested bump level."""
    major, minor, patch = _validate_semver(version)
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    if level == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if level == "none":
        return version
    raise ValueError(f"Unknown bump level: {level}")


def calculate_next_version(current_version: str, commit_messages: Sequence[str]) -> str:
    """Calculate the next semantic version from conventional commit messages."""
    return bump_version(current_version, detect_bump_level(commit_messages))


def load_project_version(root: str | Path) -> str:
    """Read the package version from ``pyproject.toml``."""
    pyproject_path = Path(root) / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def git_commit_sha(root: str | Path) -> str:
    """Return the current Git commit SHA for *root*."""
    completed = subprocess.run(
        ["git", "-C", str(Path(root)), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def collect_commit_messages(root: str | Path, since_ref: str | None = None) -> list[str]:
    """Collect commit subjects and bodies from Git for version bump calculation."""
    command = ["git", "-C", str(Path(root)), "log", "--format=%B%x1e"]
    if since_ref:
        command.insert(4, f"{since_ref}..HEAD")
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return [chunk.strip() for chunk in completed.stdout.split("\x1e") if chunk.strip()]


def resolve_release_version(root: str | Path, since_ref: str | None = None) -> str:
    """Resolve the next release version for the repository."""
    current_version = load_project_version(root)
    messages = collect_commit_messages(root, since_ref=since_ref)
    return calculate_next_version(current_version, messages)


def build_version_manifest(
    version: str,
    commit_sha: str,
    *,
    dataset_revision: str,
    build_timestamp: str | None = None,
) -> dict[str, str]:
    """Return the canonical release manifest payload."""
    return {
        "version": version,
        "build_timestamp": _normalise_timestamp(build_timestamp),
        "commit_sha": commit_sha,
        "dataset_revision": dataset_revision,
    }


def write_version_manifest(path: str | Path, manifest: dict[str, str]) -> Path:
    """Write a version manifest JSON file."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def _normalise_authors(authors: Sequence[str | dict[str, str]]) -> list[dict[str, str]]:
    rendered: list[dict[str, str]] = []
    for author in authors:
        if isinstance(author, dict):
            rendered.append(dict(author))
        else:
            rendered.append({"name": author})
    return rendered


def render_citation_cff(
    manifest: dict[str, str],
    *,
    title: str,
    authors: Sequence[str | dict[str, str]],
    repository_url: str,
    doi: str | None = None,
) -> str:
    """Render a valid ``CITATION.cff`` file from release metadata."""
    lines = [
        "cff-version: 1.2.0",
        f"message: {json.dumps('If you use this software, please cite it using the metadata below.')}",
        f"title: {json.dumps(title)}",
        f"version: {json.dumps(manifest['version'])}",
        f"date-released: {json.dumps(manifest['build_timestamp'][:10])}",
        f"repository-code: {json.dumps(repository_url)}",
    ]
    if doi is not None:
        lines.append(f"doi: {json.dumps(doi)}")
    lines.append("authors:")
    for author in _normalise_authors(authors):
        lines.append(
            "  - " + "\n    ".join(f"{key}: {json.dumps(value)}" for key, value in author.items())
        )
    return "\n".join(lines) + "\n"


def write_citation_cff(path: str | Path, citation_text: str) -> Path:
    """Write citation metadata to disk."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(citation_text, encoding="utf-8")
    return output


def render_zenodo_metadata(
    manifest: dict[str, str],
    *,
    title: str,
    authors: Sequence[str | dict[str, str]],
    description: str,
    repository_url: str,
) -> str:
    """Render the version-aligned metadata consumed by Zenodo."""
    payload = {
        "title": title,
        "version": manifest["version"],
        "upload_type": "software",
        "description": description,
        "license": "MIT",
        "creators": _normalise_authors(authors),
        "keywords": ["natural language processing", "New Zealand legislation"],
        "related_identifiers": [
            {
                "identifier": repository_url,
                "relation": "isSupplementTo",
                "scheme": "url",
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_zenodo_mirror_manifest(
    manifest: dict[str, str],
    *,
    version_doi: str | None = None,
    concept_doi: str | None = None,
    record_url: str | None = None,
    verified: bool = False,
) -> str:
    """Render DOI evidence without claiming an unverified Zenodo record."""
    if verified and (not version_doi or not concept_doi or not record_url):
        raise ValueError("verified Zenodo evidence requires both DOIs and a record URL")
    payload = {
        "schema_version": "1.0.0",
        "release_version": manifest["version"],
        "release_commit_sha": manifest["commit_sha"],
        "publication_status": "verified" if verified else "unverified",
        "verification": {
            "record_url": record_url if verified else None,
            "verified_at": manifest["build_timestamp"] if verified else None,
        },
        "version_doi": version_doi if verified else None,
        "concept_doi": concept_doi if verified else None,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def prepend_changelog_entry(
    path: str | Path,
    *,
    version: str,
    release_notes: str,
    released_at: str | None = None,
) -> Path:
    """Prepend a changelog section for a release."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    date = _normalise_timestamp(released_at)[:10]
    existing = output.read_text(encoding="utf-8") if output.is_file() else "# Changelog\n\n"
    section = f"## v{version} - {date}\n\n{release_notes.rstrip()}\n\n"
    if existing.startswith("# Changelog"):
        remainder = existing[len("# Changelog") :].lstrip("\n")
    else:
        remainder = existing
    output.write_text(f"# Changelog\n\n{section}{remainder}", encoding="utf-8")
    return output


def generate_release_assets(
    root: str | Path,
    output_dir: str | Path,
    *,
    version: str | None = None,
    dataset_revision: str = "0",
    title: str,
    authors: Sequence[str | dict[str, str]],
    repository_url: str,
    release_notes: str = "",
    doi: str | None = None,
    zenodo_description: str = "Versioned nlp-policy-nz software release.",
    zenodo_version_doi: str | None = None,
    zenodo_concept_doi: str | None = None,
    zenodo_record_url: str | None = None,
    zenodo_verified: bool = False,
    since_ref: str | None = None,
    commit_sha: str | None = None,
) -> dict[str, Path | dict[str, str] | str]:
    """Generate the release manifest, citation file, and changelog snapshot."""
    root_path = Path(root)
    resolved_version = version or resolve_release_version(root_path, since_ref=since_ref)
    resolved_commit_sha = commit_sha or git_commit_sha(root_path)
    manifest = build_version_manifest(
        resolved_version,
        resolved_commit_sha,
        dataset_revision=dataset_revision,
    )
    output_path = Path(output_dir)
    version_path = write_version_manifest(output_path / "VERSION.json", manifest)
    citation_text = render_citation_cff(
        manifest,
        title=title,
        authors=authors,
        repository_url=repository_url,
        doi=doi,
    )
    citation_path = write_citation_cff(output_path / "CITATION.cff", citation_text)
    zenodo_path = write_citation_cff(
        output_path / ".zenodo.json",
        render_zenodo_metadata(
            manifest,
            title=title,
            authors=authors,
            description=zenodo_description,
            repository_url=repository_url,
        ),
    )
    mirror_manifest_path = write_citation_cff(
        output_path / "ZENODO_MIRROR_MANIFEST.json",
        render_zenodo_mirror_manifest(
            manifest,
            version_doi=zenodo_version_doi,
            concept_doi=zenodo_concept_doi,
            record_url=zenodo_record_url,
            verified=zenodo_verified,
        ),
    )
    changelog_path = prepend_changelog_entry(
        output_path / "CHANGELOG.md",
        version=resolved_version,
        release_notes=release_notes
        or "Automated release metadata generated from release engineering workflow.",
        released_at=manifest["build_timestamp"],
    )
    return {
        "manifest": manifest,
        "version_path": version_path,
        "citation_path": citation_path,
        "zenodo_path": zenodo_path,
        "mirror_manifest_path": mirror_manifest_path,
        "changelog_path": changelog_path,
        "version": resolved_version,
    }
