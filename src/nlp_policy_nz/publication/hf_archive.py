"""Rights-safe, deterministic publication contracts for Track 90.

The module plans and stages publication locally; its explicit endpoint probe and
publication functions are the only network-capable paths.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Final
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field

from nlp_policy_nz.archive.schema import AccessClass, ArchiveBundle

CONFIG_NAMES: Final[tuple[str, ...]] = (
    "inventory",
    "documents",
    "pages",
    "blocks",
    "tokens",
    "speeches",
    "entities_relations",
    "topics_embeddings",
    "graph",
    "quality_provenance",
)

_CONFIG_KINDS: Final[dict[str, tuple[str, ...]]] = {
    "inventory": ("source", "document"),
    "documents": ("document",),
    "pages": ("page",),
    "blocks": ("region", "span", "line", "table"),
    "tokens": ("token",),
    "speeches": ("speech",),
    "entities_relations": ("assertion",),
    "topics_embeddings": ("embedding",),
    "graph": ("edge",),
    "quality_provenance": ("run",),
}


class PublicationConflictError(RuntimeError):
    """Raised when an existing staged release has a different digest."""


class PublicationPlan(BaseModel):
    """Immutable release plan consumed by publication workflows."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(pattern=r"^1\.0\.0$")
    dataset_id: str = Field(min_length=3)
    collection_id: str = Field(min_length=3)
    config_names: tuple[str, ...] = CONFIG_NAMES
    streaming: bool = True
    record_counts: dict[str, int]
    restricted_record_count: int = Field(ge=0)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_dois: tuple[str, ...] = ()
    zenodo_handoff: dict[str, str]


class PublicationVerification(BaseModel):
    """Local and endpoint evidence for one staged archive release."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_id: str
    release_dir: str
    endpoint_url: str | None = None
    endpoint_status: str = "not_run"
    manifest_matches: bool
    checksums_match: bool
    configuration_counts_match: bool
    source_projection_matches: bool
    restricted_content_absent: bool
    passed: bool
    failures: tuple[str, ...] = ()


class EndpointProbeResult(BaseModel):
    """Public Hugging Face metadata and Dataset Viewer probe result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_id: str
    metadata_url: str
    metadata_status: int
    viewer_statuses: dict[str, int]
    viewer_row_counts: dict[str, int] = Field(default_factory=dict)
    passed: bool
    failures: tuple[str, ...] = ()


def build_publication_plan(
    bundle: ArchiveBundle,
    *,
    dataset_id: str,
    collection_id: str,
    source_dois: Sequence[str] = (),
) -> PublicationPlan:
    """Build a deterministic public plan from a rights-aware archive bundle."""
    projected = bundle.public_projection()
    rows = projected.records()
    canonical = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    counts = {
        config: sum(row["kind"] in kinds for row in rows) for config, kinds in _CONFIG_KINDS.items()
    }
    restricted_count = sum(
        row["payload"].get("access_class") == AccessClass.RESTRICTED.value for row in rows
    )
    return PublicationPlan(
        schema_version="1.0.0",
        dataset_id=dataset_id,
        collection_id=collection_id,
        record_counts=counts,
        restricted_record_count=restricted_count,
        content_sha256=digest,
        source_dois=tuple(source_dois),
        zenodo_handoff={
            "upload_type": "dataset",
            "release_manifest": f"{dataset_id}/release-manifest.json",
            "content_sha256": digest,
        },
    )


def stream_config(
    bundle: ArchiveBundle, config_name: str, *, public: bool = True
) -> Iterator[dict[str, object]]:
    """Yield sorted Dataset Viewer-compatible rows for one configuration."""
    if config_name not in _CONFIG_KINDS:
        raise ValueError(f"unknown publication configuration: {config_name}")
    source = bundle.public_projection() if public else bundle
    kinds = _CONFIG_KINDS[config_name]
    yield from (row for row in source.records() if row["kind"] in kinds)


def write_release_manifest(plan: PublicationPlan, path: Path | str) -> Path:
    """Write a stable release manifest for Hugging Face and Zenodo handoff."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(plan.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def write_dataset_card(plan: PublicationPlan, path: Path | str) -> Path:
    """Write a conservative dataset card with explicit access limitations."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "configs:",
        *[
            f"- config_name: {name}\n  data_files:\n  - split: train\n    path: {name}/*.jsonl"
            for name in plan.config_names
        ],
        "---",
        "",
        f"# {plan.dataset_id}",
        "",
        "Rights-safe structured HathiTrust-NZ archive publication.",
        "",
        "## Configurations",
        "",
        *[
            f"- `{name}`: {plan.record_counts[name]} records; streaming-compatible."
            for name in plan.config_names
        ],
        "",
        "Restricted source text, alternatives, vectors, and derived text are redacted by the public projection.",
        f"Release manifest SHA-256: `{plan.content_sha256}`",
        "",
        "Source DOI references: "
        + (", ".join(plan.source_dois) if plan.source_dois else "none recorded"),
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def write_completeness_report(plan: PublicationPlan, path: Path | str) -> Path:
    """Write completeness evidence bounded to the supplied archive bundle."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "scope": "supplied ArchiveBundle",
        "status": "complete_for_supplied_bundle",
        "dataset_id": plan.dataset_id,
        "content_sha256": plan.content_sha256,
        "config_record_counts": plan.record_counts,
        "restricted_record_count": plan.restricted_record_count,
        "full_corpus_claim": False,
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def verify_materialized_publication(
    _bundle: ArchiveBundle,
    plan: PublicationPlan,
    output_dir: Path | str,
    *,
    endpoint_url: str | None = None,
    endpoint_probe: Callable[[str], bool] | None = None,
) -> PublicationVerification:
    """Verify staged release evidence without treating local files as public proof."""
    root = Path(output_dir)
    failures: list[str] = []
    manifest_matches = False
    checksums_match = False
    configuration_counts_match = False
    restricted_content_absent = False
    manifest_path = root / "release-manifest.json"
    checksum_path = root / "checksums.json"
    if manifest_path.is_file():
        manifest_matches = json.loads(manifest_path.read_text(encoding="utf-8")) == plan.model_dump(
            mode="json"
        )
    if not manifest_matches:
        failures.append("release manifest does not match publication plan")
    if checksum_path.is_file():
        expected = json.loads(checksum_path.read_text(encoding="utf-8"))
        actual = {
            str(file.relative_to(root)).replace("\\", "/"): hashlib.sha256(
                file.read_bytes()
            ).hexdigest()
            for file in sorted(root.rglob("*"))
            if file.is_file() and file != checksum_path
        }
        checksums_match = expected == actual
    if not checksums_match:
        failures.append("release checksums do not match staged files")
    expected_counts = plan.record_counts
    actual_counts: dict[str, int] = {}
    source_projection_matches = True
    restricted_content_absent = True
    for config_name in plan.config_names:
        rows = list((root / config_name).glob("part-*.jsonl"))
        count = 0
        actual_rows: list[dict[str, object]] = []
        for partition in sorted(rows):
            for line in partition.read_text(encoding="utf-8").splitlines():
                payload = json.loads(line)
                actual_rows.append(payload)
                count += 1
                row_payload = payload.get("payload", {})
                if (
                    any(
                        row_payload.get(field) not in (None, [], ())
                        for field in ("text", "alternatives", "values", "object_text")
                    )
                    and row_payload.get("access_class") == "restricted"
                ):
                    restricted_content_absent = False
        actual_counts[config_name] = count
        expected_rows = list(stream_config(_bundle, config_name))
        if actual_rows != expected_rows:
            source_projection_matches = False
    configuration_counts_match = actual_counts == expected_counts
    if not configuration_counts_match:
        failures.append("materialized configuration counts do not match the plan")
    if not source_projection_matches:
        failures.append("materialized rows do not match the source public projection")
    if not restricted_content_absent:
        failures.append("restricted content is present in the staged projection")
    endpoint_status = "not_run"
    if endpoint_url is not None:
        endpoint_status = (
            "passed" if endpoint_probe is not None and endpoint_probe(endpoint_url) else "failed"
        )
        if endpoint_status != "passed":
            failures.append("endpoint smoke probe was not successful")
    return PublicationVerification(
        dataset_id=plan.dataset_id,
        release_dir=str(root),
        endpoint_url=endpoint_url,
        endpoint_status=endpoint_status,
        manifest_matches=manifest_matches,
        checksums_match=checksums_match,
        configuration_counts_match=configuration_counts_match,
        source_projection_matches=source_projection_matches,
        restricted_content_absent=restricted_content_absent,
        passed=not failures,
        failures=tuple(failures),
    )


def write_publication_verification(report: PublicationVerification, path: Path | str) -> Path:
    """Write machine-readable Track 90 acceptance evidence."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def probe_huggingface_endpoint(
    dataset_id: str,
    *,
    configs: Sequence[str] = CONFIG_NAMES,
    timeout: float = 15.0,
    opener: Callable[..., object] = urlopen,
) -> EndpointProbeResult:
    """Probe public Hub metadata and Dataset Viewer rows without credentials."""
    encoded_id = quote(dataset_id, safe="/")
    metadata_url = f"https://huggingface.co/api/datasets/{encoded_id}"
    viewer_statuses: dict[str, int] = {}
    viewer_row_counts: dict[str, int] = {}
    failures: list[str] = []

    def response(url: str) -> tuple[int, bytes]:
        request = Request(  # noqa: S310
            url, headers={"User-Agent": "nlp-policy-nz-track90-probe/1.0"}
        )
        try:
            with opener(request, timeout=timeout) as response:  # type: ignore[union-attr]
                return int(response.status), response.read()  # type: ignore[union-attr]
        except HTTPError as error:
            return error.code, b""
        except URLError:
            return 0, b""

    metadata_status, _ = response(metadata_url)
    if metadata_status != 200:
        failures.append(f"metadata endpoint returned HTTP {metadata_status}")
    for config in configs:
        viewer_url = (
            "https://datasets-server.huggingface.co/first-rows?dataset="
            f"{encoded_id}&config={quote(config)}&split=train"
        )
        viewer_statuses[config], body = response(viewer_url)
        if viewer_statuses[config] != 200:
            failures.append(f"Dataset Viewer config {config} returned HTTP {viewer_statuses[config]}")
            continue
        try:
            payload = json.loads(body.decode("utf-8"))
            rows = payload.get("rows")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            rows = None
        if not isinstance(rows, list):
            failures.append(f"Dataset Viewer config {config} returned no JSON rows")
        else:
            viewer_row_counts[config] = len(rows)
    return EndpointProbeResult(
        dataset_id=dataset_id,
        metadata_url=metadata_url,
        metadata_status=metadata_status,
        viewer_statuses=viewer_statuses,
        viewer_row_counts=viewer_row_counts,
        passed=not failures,
        failures=tuple(failures),
    )


def write_endpoint_probe(report: EndpointProbeResult, path: Path | str) -> Path:
    """Write machine-readable public endpoint evidence."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def write_zenodo_handoff(plan: PublicationPlan, path: Path | str) -> Path:
    """Write metadata suitable for a separate Zenodo deposition job."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "title": f"{plan.dataset_id} structured archive release",
        "upload_type": "dataset",
        "dataset_id": plan.dataset_id,
        "collection_id": plan.collection_id,
        "related_identifiers": list(plan.source_dois),
        "release_manifest_sha256": plan.content_sha256,
        "publication_policy": "public projection only; restricted text is redacted",
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_provenance_attestation(plan: PublicationPlan, path: Path | str) -> Path:
    """Write a minimal in-toto-style subject attestation for the release."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [{"name": plan.dataset_id, "digest": {"sha256": plan.content_sha256}}],
        "predicate": {
            "builder": {"id": "https://github.com/actions/runner"},
            "buildType": "track90-hf-archive",
        },
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_software_bill_of_materials(path: Path | str) -> Path:
    """Write a deterministic CycloneDX inventory of the publishing runtime."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    components = []
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name") or distribution.metadata.get("name")
        if not name:
            continue
        components.append(
            {
                "type": "library",
                "name": name,
                "version": distribution.version,
                "purl": f"pkg:pypi/{name.casefold()}@{distribution.version}",
            }
        )
    components.sort(key=lambda component: (component["name"].casefold(), component["version"]))
    target.write_text(
        json.dumps(
            {
                "bomFormat": "CycloneDX",
                "specVersion": "1.5",
                "version": 1,
                "components": components,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def write_checksums(directory: Path | str, path: Path | str) -> Path:
    """Write SHA-256 checksums for all staged files except the checksum file."""
    root = Path(directory)
    target = Path(path)
    files = sorted(file for file in root.rglob("*") if file.is_file() and file != target)
    payload = {
        str(file.relative_to(root)).replace("\\", "/"): hashlib.sha256(
            file.read_bytes()
        ).hexdigest()
        for file in files
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def materialize_publication(
    bundle: ArchiveBundle,
    plan: PublicationPlan,
    output_dir: Path | str,
    *,
    partition_size: int = 100_000,
) -> Path:
    """Write deterministic JSONL partitions and publication metadata."""
    if partition_size < 1:
        raise ValueError("partition_size must be positive")
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    for config_name in plan.config_names:
        config_dir = target / config_name
        config_dir.mkdir(parents=True, exist_ok=True)
        partition = 0
        rows_in_partition = 0
        handle = (config_dir / f"part-{partition:05d}.jsonl").open("w", encoding="utf-8")
        try:
            for row in stream_config(bundle, config_name):
                if rows_in_partition >= partition_size:
                    handle.close()
                    partition += 1
                    rows_in_partition = 0
                    handle = (config_dir / f"part-{partition:05d}.jsonl").open(
                        "w", encoding="utf-8"
                    )
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                rows_in_partition += 1
        finally:
            handle.close()
    write_release_manifest(plan, target / "release-manifest.json")
    write_dataset_card(plan, target / "README.md")
    stage_publication(plan, target / "publication-state.json")
    write_zenodo_handoff(plan, target / "zenodo-handoff.json")
    write_provenance_attestation(plan, target / "provenance-attestation.json")
    write_software_bill_of_materials(target / "sbom.json")
    write_completeness_report(plan, target / "completeness-report.json")
    write_checksums(target, target / "checksums.json")
    return target


def publish_hf_archive(
    bundle: ArchiveBundle,
    plan: PublicationPlan,
    output_dir: Path | str,
    *,
    token: str | None = None,
    dry_run: bool = True,
    endpoint_probe: Callable[[str], bool] | None = None,
) -> str:
    """Materialize and optionally upload a complete multi-config Hub dataset."""
    materialized = materialize_publication(bundle, plan, output_dir)
    verification = verify_materialized_publication(bundle, plan, materialized)
    write_publication_verification(verification, materialized / "verification.json")
    if not verification.passed:
        raise ValueError("local publication verification failed: " + "; ".join(verification.failures))
    if dry_run:
        return f"dry-run://huggingface.co/datasets/{plan.dataset_id}"
    if not token:
        raise ValueError("HF token is required for a non-dry-run publication")
    from huggingface_hub import HfApi  # noqa: PLC0415

    api = HfApi(token=token)
    repository_exists = True
    if hasattr(api, "repo_info"):
        try:
            api.repo_info(repo_id=plan.dataset_id, repo_type="dataset")
        except Exception:  # noqa: BLE001
            repository_exists = False
    api.create_repo(repo_id=plan.dataset_id, repo_type="dataset", exist_ok=True)
    try:
        api.upload_folder(
            repo_id=plan.dataset_id,
            repo_type="dataset",
            folder_path=str(materialized),
            commit_message=f"Publish archive release {plan.content_sha256[:12]}",
        )
        if endpoint_probe is not None and not endpoint_probe(plan.dataset_id):
            raise RuntimeError("public endpoint verification failed after upload")
    except Exception:
        if not repository_exists and hasattr(api, "delete_repo"):
            api.delete_repo(repo_id=plan.dataset_id, repo_type="dataset")
        raise
    return f"https://huggingface.co/datasets/{plan.dataset_id}"


def stage_publication(plan: PublicationPlan, path: Path | str) -> Path:
    """Persist an idempotent staged state; never silently replace a release."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "dataset_id": plan.dataset_id,
        "content_sha256": plan.content_sha256,
        "status": "staged",
    }
    if target.exists():
        current = json.loads(target.read_text(encoding="utf-8"))
        if current != state:
            raise PublicationConflictError(f"staged publication conflict: {target}")
        return target
    target.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


__all__ = [
    "CONFIG_NAMES",
    "EndpointProbeResult",
    "PublicationConflictError",
    "PublicationPlan",
    "PublicationVerification",
    "build_publication_plan",
    "materialize_publication",
    "probe_huggingface_endpoint",
    "publish_hf_archive",
    "stage_publication",
    "stream_config",
    "verify_materialized_publication",
    "write_checksums",
    "write_completeness_report",
    "write_dataset_card",
    "write_endpoint_probe",
    "write_provenance_attestation",
    "write_publication_verification",
    "write_release_manifest",
    "write_software_bill_of_materials",
    "write_zenodo_handoff",
]
