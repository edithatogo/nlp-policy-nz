"""Deterministic archive bundle serializers and rights-safe projections."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.archive.schema import ArchiveBundle


def write_json(bundle: ArchiveBundle, path: str | Path, *, public: bool = True) -> Path:
    """Write a canonical JSON bundle."""
    bundle = _for_export(bundle, public)
    destination = _prepare(path)
    destination.write_text(
        json.dumps(bundle.model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return destination


def write_jsonl(bundle: ArchiveBundle, path: str | Path, *, public: bool = True) -> Path:
    """Write sorted typed archive records as JSONL."""
    bundle = _for_export(bundle, public)
    destination = _prepare(path)
    destination.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in bundle.records()
        ),
        encoding="utf-8",
    )
    return destination


def write_jsonld(bundle: ArchiveBundle, path: str | Path, *, public: bool = True) -> Path:
    """Write a deterministic JSON-LD graph view."""
    bundle = _for_export(bundle, public)
    destination = _prepare(path)
    graph = [
        {
            "@id": f"urn:nlp-policy-nz:{row['kind']}:{row['id']}",
            "@type": f"hathi:{row['kind']}",
            **row["payload"],
        }
        for row in bundle.records()
    ]
    destination.write_text(
        json.dumps(
            {
                "@context": {"hathi": "https://example.org/nlp-policy-nz/archive#"},
                "@graph": graph,
                "schemaVersion": bundle.schema_version,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return destination


def write_rdf(bundle: ArchiveBundle, path: str | Path, *, public: bool = True) -> Path:
    """Write a compact RDF/Turtle graph without exposing a restricted projection."""
    bundle = _for_export(bundle, public)
    destination = _prepare(path)
    lines = [
        "@prefix hathi: <https://example.org/nlp-policy-nz/archive#> .",
        "@prefix schema: <https://schema.org/> .",
        "",
    ]
    for row in bundle.records():
        subject = f"<urn:nlp-policy-nz:{row['kind']}:{row['id']}>"
        lines.append(f'{subject} a hathi:{row["kind"]}; schema:identifier "{row["id"]}" .')
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return destination


def write_markdown(bundle: ArchiveBundle, path: str | Path, *, public: bool = True) -> Path:
    """Write an operator-readable schema inventory without source payloads."""
    bundle = _for_export(bundle, public)
    destination = _prepare(path)
    counts: dict[str, int] = {}
    for row in bundle.records():
        counts[row["kind"]] = counts.get(row["kind"], 0) + 1
    content = [
        "# Archive Bundle",
        "",
        f"- Schema version: `{bundle.schema_version}`",
        f"- Record count: `{len(bundle.records())}`",
        "",
        "## Layers",
        "",
    ]
    content.extend(f"- `{kind}`: {counts[kind]}" for kind in sorted(counts))
    destination.write_text("\n".join(content) + "\n", encoding="utf-8")
    return destination


def write_parquet(bundle: ArchiveBundle, path: str | Path, *, public: bool = True) -> Path:
    """Write typed archive rows to Parquet using the optional Arrow runtime."""
    import pyarrow as pa
    from pyarrow import parquet

    bundle = _for_export(bundle, public)
    destination = _prepare(path)
    rows = [
        {
            "kind": row["kind"],
            "id": row["id"],
            "payload_json": json.dumps(row["payload"], sort_keys=True),
        }
        for row in bundle.records()
    ]
    parquet.write_table(pa.Table.from_pylist(rows), destination)
    return destination


def _prepare(path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def _for_export(bundle: ArchiveBundle, public: bool) -> ArchiveBundle:
    """Apply the fail-closed public projection unless explicitly disabled."""
    return bundle.public_projection() if public else bundle


__all__ = [
    "write_json",
    "write_jsonl",
    "write_jsonld",
    "write_markdown",
    "write_parquet",
    "write_rdf",
]
