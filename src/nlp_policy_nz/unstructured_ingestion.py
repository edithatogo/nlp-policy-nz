"""Optional Unstructured-backed ingestion adapter for messy documents."""

from __future__ import annotations

import json
import typing as ty
from pathlib import Path

from nlp_policy_nz.universal_framework_v3 import DocumentChunk, UniversalIngestionEngine

try:
    from unstructured.partition.auto import partition as _partition_document
except ImportError:  # pragma: no cover - exercised in dependency-missing tests.
    _partition_document = None

_PartitionCallable = ty.Callable[..., ty.Iterable[object]]


def _require_partition() -> _PartitionCallable:
    """Return the optional partition callable or raise a clear install hint."""
    if _partition_document is None:
        msg = (
            "Unstructured support is not installed. Install the optional "
            "'unstructured' extra to enable the adapter."
        )
        raise ImportError(msg)
    return ty.cast("_PartitionCallable", _partition_document)


def _stringify_value(value: object) -> str:
    """Return a stable string representation for metadata values."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, sort_keys=True, default=str)
    return str(value)


def _metadata_mapping(metadata: object) -> dict[str, str]:
    """Normalize unstructured metadata into the adapter's string map."""
    if metadata is None:
        return {}
    if hasattr(metadata, "to_dict"):
        raw = ty.cast("ty.Callable[[], object]", metadata.to_dict)()
    elif isinstance(metadata, dict):
        raw = metadata
    else:
        raw = {}
    if not isinstance(raw, dict):
        return {}
    items = ty.cast("dict[object, object]", raw).items()
    return {str(key): _stringify_value(value) for key, value in items}


def _element_label(element: object) -> str:
    """Derive the structural label that best matches the unstructured element."""
    category = getattr(element, "category", None)
    if isinstance(category, str) and category:
        return category
    text_type = element.__class__.__name__.removesuffix("Element")
    return text_type or "unstructured"


def _quality_flags(text: str, metadata: dict[str, str]) -> str:
    """Summarize the adapter-specific quality flags as a stable string."""
    flags: list[str] = ["unstructured"]
    if text.strip():
        flags.append("text_present")
    if metadata.get("page_number"):
        flags.append(f"page:{metadata['page_number']}")
    if metadata.get("filetype"):
        flags.append(f"filetype:{metadata['filetype']}")
    if metadata.get("coordinates"):
        flags.append("layout")
    return json.dumps(flags, sort_keys=True)


def compare_with_html_parser(
    source_path: str | Path,
    *,
    strategy: str | None = None,
    **partition_kwargs: object,
) -> dict[str, object]:
    """Compare the optional adapter against the canonical HTML parser."""
    from nlp_policy_nz.universal_framework_v3 import get_ingestion_engine

    path = Path(source_path)
    adapter = UnstructuredIngestionEngine(strategy=strategy or "auto")
    adapter_chunks = adapter.ingest_file(path, strategy=strategy, **partition_kwargs)
    canonical_chunks = get_ingestion_engine("HTML").ingest(path.read_text(encoding="utf-8"))

    adapter_ids = [chunk.chunk_id for chunk in adapter_chunks]
    canonical_ids = [chunk.chunk_id for chunk in canonical_chunks]
    shared_ids = [chunk_id for chunk_id in adapter_ids if chunk_id in canonical_ids]

    return {
        "source_path": str(path),
        "adapter_chunk_count": len(adapter_chunks),
        "canonical_chunk_count": len(canonical_chunks),
        "adapter_chunk_ids": adapter_ids,
        "canonical_chunk_ids": canonical_ids,
        "shared_chunk_ids": shared_ids,
        "adapter_only_chunk_ids": [chunk_id for chunk_id in adapter_ids if chunk_id not in canonical_ids],
        "canonical_only_chunk_ids": [
            chunk_id for chunk_id in canonical_ids if chunk_id not in adapter_ids
        ],
    }


class UnstructuredIngestionEngine(UniversalIngestionEngine):
    """Optional adapter that partitions local files with Unstructured."""

    def __init__(self, *, strategy: str = "auto") -> None:
        self.strategy = strategy

    def ingest(self, raw_data: str) -> list[DocumentChunk]:
        """Treat the input string as a local file path and partition it."""
        return self.ingest_file(Path(raw_data))

    def ingest_file(
        self,
        source_path: str | Path,
        *,
        strategy: str | None = None,
        **partition_kwargs: object,
    ) -> list[DocumentChunk]:
        """Partition a local file into document chunks."""
        path = Path(source_path)
        if not path.exists():
            msg = f"Unstructured adapter expects an existing local file: {path}"
            raise FileNotFoundError(msg)

        partition = _require_partition()
        elements = partition(
            filename=str(path),
            strategy=strategy or self.strategy,
            **partition_kwargs,
        )

        chunks: list[DocumentChunk] = []
        for index, element in enumerate(elements):
            text = _stringify_value(getattr(element, "text", ""))
            metadata = _metadata_mapping(getattr(element, "metadata", None))
            metadata.update(
                {
                    "source_path": str(path),
                    "adapter": "unstructured",
                    "partition_strategy": strategy or self.strategy,
                    "quality_flags": _quality_flags(text, metadata),
                }
            )
            chunks.append(
                DocumentChunk(
                    chunk_id=_stringify_value(
                        metadata.get("element_id") or metadata.get("id") or f"unstructured-{index}"
                    ),
                    text=text,
                    structural_type=_element_label(element),
                    attributes=metadata,
                )
            )
        return chunks


__all__ = ["UnstructuredIngestionEngine", "compare_with_html_parser"]
