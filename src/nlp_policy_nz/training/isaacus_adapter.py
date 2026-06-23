"""Offline Isaacus ecosystem integration helpers for Track 22."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Literal

from nlp_policy_nz.storage import PipelineRecord

AssetKind = Literal["corpus", "qa", "rag-bench", "retrieval-bench"]
AccessMode = Literal["open-hf", "api-or-airgapped", "repository-monitor"]


@dataclass(frozen=True)
class IsaacusDatasetManifest:
    """Repository-side manifest entry for an Isaacus dataset."""

    id: str
    hf_id: str
    kind: AssetKind
    expected_records: int
    jurisdictions: tuple[str, ...]
    required_fields: tuple[str, ...]
    purpose: str


@dataclass(frozen=True)
class IsaacusModelManifest:
    """Repository-side manifest entry for an Isaacus model or API model."""

    id: str
    hf_id: str | None
    model_type: str
    params: str | None
    license: str | None
    access_mode: AccessMode
    evaluation_tasks: tuple[str, ...]
    purpose: str


@dataclass(frozen=True)
class IsaacusToolManifest:
    """Repository-side manifest entry for an Isaacus tool."""

    id: str
    repository: str
    integration_action: Literal["evaluate", "monitor"]
    purpose: str


@dataclass(frozen=True)
class IsaacusRecord:
    """Normalised Australian legal source row before pipeline conversion."""

    source_id: str
    doc_id: str
    text: str
    jurisdiction: str
    title: str | None = None
    citations: tuple[str, ...] = ()
    source_url: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class MlebNzQuery:
    """Single NZ-MLEB retrieval query scaffold."""

    query_id: str
    query_text: str
    relevant_doc_ids: tuple[str, ...]
    jurisdiction: str
    task: str


@dataclass(frozen=True)
class IsaacusAccessGate:
    """Explicit external-access switches for downloads and proprietary APIs."""

    allow_network: bool = False
    allow_proprietary_api: bool = False


def default_isaacus_datasets() -> dict[str, IsaacusDatasetManifest]:
    """Return the Track 22 Isaacus dataset registry."""
    manifests = [
        IsaacusDatasetManifest(
            id="open-australian-legal-corpus",
            hf_id="isaacus/open-australian-legal-corpus",
            kind="corpus",
            expected_records=147_000,
            jurisdictions=("AU", "Cth", "NSW", "VIC", "QLD", "WA", "SA"),
            required_fields=("id", "text", "jurisdiction"),
            purpose="Cross-jurisdiction AU to NZ legal-language pretraining.",
        ),
        IsaacusDatasetManifest(
            id="open-australian-legal-qa",
            hf_id="isaacus/open-australian-legal-qa",
            kind="qa",
            expected_records=2_100,
            jurisdictions=("AU",),
            required_fields=("question", "answer", "context"),
            purpose="Template for NZ legal QA generation and evaluation.",
        ),
        IsaacusDatasetManifest(
            id="legal-rag-bench",
            hf_id="isaacus/legal-rag-bench",
            kind="rag-bench",
            expected_records=4_900,
            jurisdictions=("AU", "multi"),
            required_fields=("query", "answer", "contexts"),
            purpose="End-to-end legal RAG benchmark comparison.",
        ),
        IsaacusDatasetManifest(
            id="mleb-legal-rag-bench",
            hf_id="isaacus/mleb-legal-rag-bench",
            kind="retrieval-bench",
            expected_records=5_000,
            jurisdictions=("multi",),
            required_fields=("query", "relevant_doc_ids"),
            purpose="Base methodology for an NZ-MLEB retrieval extension.",
        ),
    ]
    return {manifest.id: manifest for manifest in manifests}


def default_isaacus_models() -> dict[str, IsaacusModelManifest]:
    """Return the Track 22 Isaacus model registry."""
    manifests = [
        IsaacusModelManifest(
            id="open-australian-legal-llm",
            hf_id="isaacus/open-australian-legal-llm",
            model_type="causal-lm",
            params="1.5B",
            license="Apache-2.0",
            access_mode="open-hf",
            evaluation_tasks=("zero-shot-nz-legal", "au-to-nz-transfer"),
            purpose="Primary AU to NZ domain-transfer baseline.",
        ),
        IsaacusModelManifest(
            id="open-australian-legal-gpt2",
            hf_id="isaacus/open-australian-legal-gpt2",
            model_type="causal-lm",
            params="124M",
            license="Apache-2.0",
            access_mode="open-hf",
            evaluation_tasks=("small-baseline", "citation-extraction"),
            purpose="Small local baseline for fast iteration.",
        ),
        IsaacusModelManifest(
            id="emubert",
            hf_id="isaacus/emubert",
            model_type="masked-lm",
            params="124M",
            license="Apache-2.0",
            access_mode="open-hf",
            evaluation_tasks=("encoding", "mlm", "document-similarity"),
            purpose="Legal-domain encoder comparison.",
        ),
        IsaacusModelManifest(
            id="kanon-2-tokenizer",
            hf_id="isaacus/kanon-2-tokenizer",
            model_type="tokenizer",
            params=None,
            license=None,
            access_mode="open-hf",
            evaluation_tasks=("maori-token-preservation", "legal-tokenisation"),
            purpose="Tokenizer comparison against the NZ tokenizer guard.",
        ),
        IsaacusModelManifest(
            id="kanon-2-embedder",
            hf_id=None,
            model_type="embedding-api",
            params=None,
            license="proprietary",
            access_mode="api-or-airgapped",
            evaluation_tasks=("citation-search", "document-similarity", "nz-mleb"),
            purpose="High-performing MLEB embedding backend candidate.",
        ),
    ]
    return {manifest.id: manifest for manifest in manifests}


def default_isaacus_tools() -> dict[str, IsaacusToolManifest]:
    """Return the Track 22 Isaacus tool registry."""
    manifests = [
        IsaacusToolManifest(
            id="semchunk",
            repository="github.com/isaacus-dev/semchunk",
            integration_action="evaluate",
            purpose="Compare semantic legal chunking with syntactic/chunking.py.",
        ),
        IsaacusToolManifest(
            id="blackstone-graph",
            repository="github.com/isaacus-dev",
            integration_action="monitor",
            purpose="Track stable Blackstone Graph release for graph integration.",
        ),
    ]
    return {manifest.id: manifest for manifest in manifests}


def _normalise_text(value: str) -> str:
    """Normalise text to NFC and collapse intra-paragraph whitespace."""
    normalised = unicodedata.normalize("NFC", value)
    paragraphs = [
        re.sub(r"[ \t\r\f\v]+", " ", paragraph).strip()
        for paragraph in re.split(r"\n\s*\n", normalised)
    ]
    return "\n\n".join(paragraph for paragraph in paragraphs if paragraph)


def _as_tuple(value: object) -> tuple[str, ...]:
    """Coerce a scalar or iterable citation value into a string tuple."""
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if isinstance(value, Iterable):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),)


def normalize_isaacus_record(
    source_id: str,
    row: Mapping[str, object],
) -> IsaacusRecord:
    """Normalise an Isaacus dataset row before pipeline conversion.

    Args:
        source_id: Short Isaacus dataset identifier.
        row: Raw dataset row from Hugging Face or a local export.

    Returns:
        A normalised Isaacus source record.

    Raises:
        ValueError: If a document identifier or text body is missing.

    """
    doc_id = str(row.get("id") or row.get("doc_id") or row.get("record_id") or "").strip()
    text = str(row.get("text") or row.get("body") or row.get("context") or "").strip()
    if not doc_id:
        raise ValueError("Isaacus row is missing a document identifier")
    if not text:
        raise ValueError("Isaacus row is missing text")

    jurisdiction = str(row.get("jurisdiction") or row.get("court") or "AU").strip()
    citations = _as_tuple(row.get("citations") or row.get("citation") or row.get("legal_citations"))
    return IsaacusRecord(
        source_id=source_id,
        doc_id=doc_id,
        text=_normalise_text(text),
        jurisdiction=jurisdiction,
        title=(str(row["title"]).strip() if row.get("title") else None),
        citations=citations,
        source_url=(str(row["source_url"]).strip() if row.get("source_url") else None),
        metadata={key: value for key, value in row.items() if key not in {"text", "body"}},
    )


def to_pipeline_record(record: IsaacusRecord) -> PipelineRecord:
    """Convert a normalised Isaacus record into the existing pipeline schema."""
    tokens = re.findall(r"\b[\w\u0100-\u017F]+\b", record.text, flags=re.UNICODE)
    te_reo_terms = [
        token
        for token in tokens
        if any(char in token for char in "āēīōūĀĒĪŌŪ")
    ]
    return PipelineRecord(
        doc_id=f"isaacus:{record.source_id}:{record.doc_id}",
        corpus_source=f"isaacus:au:{record.jurisdiction}",
        raw_text=record.text,
        cleaned_tokens=tokens,
        nz_act_citations=list(record.citations),
        te_reo_terms=te_reo_terms,
        report_title=record.title,
    )


def normalize_isaacus_records(
    source_id: str,
    rows: Iterable[Mapping[str, object]],
) -> list[PipelineRecord]:
    """Normalise multiple Isaacus rows directly into pipeline records."""
    return [to_pipeline_record(normalize_isaacus_record(source_id, row)) for row in rows]


def make_nz_mleb_query(
    *,
    query_id: str,
    query_text: str,
    relevant_doc_ids: Sequence[str],
    jurisdiction: str,
    task: str,
) -> MlebNzQuery:
    """Create one NZ-MLEB retrieval query with relevance judgements."""
    relevant = tuple(doc_id for doc_id in relevant_doc_ids if doc_id)
    if not relevant:
        raise ValueError("NZ-MLEB query requires at least one relevant document")
    return MlebNzQuery(
        query_id=query_id,
        query_text=_normalise_text(query_text),
        relevant_doc_ids=relevant,
        jurisdiction=jurisdiction,
        task=task,
    )


def require_external_access(
    gate: IsaacusAccessGate,
    *,
    needs_network: bool,
    needs_proprietary_api: bool,
) -> None:
    """Fail closed for download/API operations unless explicitly enabled."""
    if needs_network and not gate.allow_network:
        raise PermissionError("Isaacus operation requires explicit network access")
    if needs_proprietary_api and not gate.allow_proprietary_api:
        raise PermissionError("Isaacus operation requires proprietary API access")


def render_isaacus_integration_report() -> str:
    """Render a repo-side Isaacus integration report."""
    datasets = default_isaacus_datasets()
    models = default_isaacus_models()
    tools = default_isaacus_tools()
    lines = [
        "# Isaacus Legal NLP Ecosystem Integration",
        "",
        "This is a repo-side integration scaffold. No Isaacus datasets or models "
        "are downloaded by this report; external downloads, API calls, and "
        "fine-tuning runs require explicit access gates.",
        "",
        "## Dataset Manifests",
        "",
        "| ID | HF ID | Kind | Expected records | Purpose |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for manifest in datasets.values():
        lines.append(
            f"| {manifest.id} | {manifest.hf_id} | {manifest.kind} | "
            f"{manifest.expected_records} | {manifest.purpose} |"
        )

    lines.extend(
        [
            "",
            "## Model Evaluation Targets",
            "",
            "| ID | Access | Tasks | Purpose |",
            "| --- | --- | --- | --- |",
        ]
    )
    for manifest in models.values():
        lines.append(
            f"| {manifest.id} | {manifest.access_mode} | "
            f"{', '.join(manifest.evaluation_tasks)} | {manifest.purpose} |"
        )

    lines.extend(
        [
            "",
            "## Tool Integration Targets",
            "",
            "| ID | Action | Repository | Purpose |",
            "| --- | --- | --- | --- |",
        ]
    )
    for manifest in tools.values():
        lines.append(
            f"| {manifest.id} | {manifest.integration_action} | "
            f"{manifest.repository} | {manifest.purpose} |"
        )

    lines.extend(
        [
            "",
            "## Next External Gates",
            "",
            "- Download Isaacus datasets into a local cache with recorded hashes.",
            "- Convert AU records with `normalize_isaacus_records` and persist "
            "merged NZ-AU Parquet outputs.",
            "- Run Kanon 2, EmuBERT, and Open Australian Legal LLM evaluations "
            "only after access credentials and benchmark artefact paths are set.",
            "- Publish NZ-MLEB baselines from measured retrieval outputs.",
        ]
    )
    return "\n".join(lines) + "\n"


def _manifest_payload() -> dict[str, dict[str, dict[str, object]]]:
    """Return JSON-serialisable Isaacus manifests."""
    return {
        "datasets": {
            key: asdict(value) for key, value in default_isaacus_datasets().items()
        },
        "models": {
            key: asdict(value) for key, value in default_isaacus_models().items()
        },
        "tools": {
            key: asdict(value) for key, value in default_isaacus_tools().items()
        },
    }


def render_isaacus_manifest_json() -> str:
    """Render the offline Isaacus manifest as formatted JSON."""
    return json.dumps(_manifest_payload(), indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Run the offline Isaacus adapter CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-manifest", action="store_true")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args(argv)

    if args.print_manifest:
        sys.stdout.write(render_isaacus_manifest_json())
        return 0
    if args.report:
        sys.stdout.write(render_isaacus_integration_report())
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
