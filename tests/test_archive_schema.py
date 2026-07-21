from __future__ import annotations

import json
from pathlib import Path

import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError

from nlp_policy_nz.archive.migrations import migrate_bundle
from nlp_policy_nz.archive.schema import (
    AccessClass,
    ArchiveAssertion,
    ArchiveBundle,
    ArchiveDocument,
    ArchiveEmbedding,
    ArchiveGraphEdge,
    ArchiveLine,
    ArchivePage,
    ArchiveRegion,
    ArchiveRun,
    ArchiveSource,
    ArchiveSpan,
    ArchiveSpeech,
    ArchiveTable,
    ArchiveToken,
    CoordinateBox,
    stable_id,
)
from nlp_policy_nz.archive.serializers import (
    write_json,
    write_jsonl,
    write_jsonld,
    write_markdown,
    write_parquet,
    write_rdf,
)


def _bundle(*, restricted: bool = False) -> ArchiveBundle:
    access = AccessClass.RESTRICTED if restricted else AccessClass.PUBLIC
    source = ArchiveSource(
        source_id="source-1",
        uri="https://example.test/source-1",
        sha256="a" * 64,
        access_class=access,
        rights_code="17",
    )
    document = ArchiveDocument(document_id="doc-1", source_id=source.source_id, title="Hansard")
    page = ArchivePage(
        page_id="page-1",
        document_id=document.document_id,
        page_number=1,
        original_bbox=CoordinateBox(x0=0, y0=0, x1=100, y1=200, space="original"),
        normalized_bbox=CoordinateBox(x0=0, y0=0, x1=1, y1=1, space="normalized"),
    )
    region = ArchiveRegion(region_id="region-1", page_id=page.page_id, kind="paragraph")
    span = ArchiveSpan(
        span_id="span-1",
        page_id=page.page_id,
        start=0,
        end=5,
        text=None if restricted else "Hello",
        access_class=access,
    )
    line = ArchiveLine(
        line_id="line-1",
        region_id=region.region_id,
        span_id=span.span_id,
        text=None if restricted else "Hello",
        access_class=access,
    )
    token = ArchiveToken(
        token_id="token-1",
        line_id=line.line_id,
        text=None if restricted else "Hello",
        confidence=0.9,
        alternatives=("Helo",),
        access_class=access,
    )
    speech = ArchiveSpeech(
        speech_id="speech-1",
        page_id=page.page_id,
        text=None if restricted else "Hello",
        span_ids=(span.span_id,),
        access_class=access,
    )
    table = ArchiveTable(
        table_id="table-1",
        page_id=page.page_id,
        span_ids=(span.span_id,),
        cell_count=1,
        access_class=access,
    )
    embedding = ArchiveEmbedding(
        embedding_id="embedding-1",
        target_id=speech.speech_id,
        model_id="model-1",
        vector_dim=2,
        values=(0.1, 0.2),
        access_class=access,
    )
    assertion = ArchiveAssertion(
        assertion_id="assertion-1",
        subject_id=speech.speech_id,
        predicate="mentions",
        object_text=None if restricted else "Hello",
        span_ids=(span.span_id,),
        access_class=access,
    )
    edge = ArchiveGraphEdge(
        edge_id="edge-1",
        subject_id=speech.speech_id,
        predicate="mentions",
        object_id=assertion.assertion_id,
    )
    run = ArchiveRun(
        run_id="run-1",
        schema_version="1.0.0",
        commit_sha="b" * 40,
        source_ids=(source.source_id,),
    )
    return ArchiveBundle(
        schema_version="1.0.0",
        sources=(source,),
        documents=(document,),
        pages=(page,),
        regions=(region,),
        spans=(span,),
        lines=(line,),
        tokens=(token,),
        speeches=(speech,),
        tables=(table,),
        embeddings=(embedding,),
        assertions=(assertion,),
        graph_edges=(edge,),
        runs=(run,),
    )


def test_stable_ids_and_coordinate_validation() -> None:
    assert stable_id("page", "doc-1", "1") == stable_id("page", "doc-1", "1")
    with pytest.raises(ValidationError):
        CoordinateBox(x0=1, y0=0, x1=1, y1=1, space="normalized")
    with pytest.raises(ValidationError):
        CoordinateBox(x0=2, y0=0, x1=1, y1=1, space="original")
    with pytest.raises(ValidationError):
        CoordinateBox(x0=0, y0=2, x1=1, y1=1, space="original")


@given(st.from_regex(r"[a-zA-Z0-9]{1,20}", fullmatch=True))
def test_stable_id_is_repeatable_for_arbitrary_identity(value: str) -> None:
    assert stable_id("token", value) == stable_id("token", value)


def test_bundle_enforces_referential_integrity() -> None:
    bundle = _bundle()
    with pytest.raises(ValidationError, match="unknown region"):
        ArchiveBundle.model_validate(
            bundle.model_dump(mode="python")
            | {"lines": [{**bundle.lines[0].model_dump(), "region_id": "missing"}]}
        )
    with pytest.raises(ValidationError, match="unknown subject"):
        ArchiveBundle.model_validate(
            bundle.model_dump(mode="python")
            | {"assertions": [{**bundle.assertions[0].model_dump(), "subject_id": "missing"}]}
        )


def test_public_projection_redacts_restricted_text_but_retains_lineage() -> None:
    projected = _bundle(restricted=True).public_projection()

    assert projected.sources[0].source_id == "source-1"
    assert projected.pages[0].page_id == "page-1"
    assert projected.spans[0].text is None
    assert projected.lines[0].text is None
    assert projected.tokens[0].text is None
    assert projected.speeches[0].text is None
    assert projected.assertions[0].object_text is None


def test_public_projection_propagates_restricted_source_to_public_default_children(
    tmp_path: Path,
) -> None:
    payload = _bundle().model_dump(mode="python")
    payload["sources"][0]["access_class"] = AccessClass.RESTRICTED
    bundle = ArchiveBundle.model_validate(payload)

    projected = bundle.public_projection()

    assert projected.documents[0].title is None
    assert projected.spans[0].access_class is AccessClass.RESTRICTED
    assert projected.spans[0].text is None
    assert projected.lines[0].access_class is AccessClass.RESTRICTED
    assert projected.lines[0].text is None
    assert projected.tokens[0].access_class is AccessClass.RESTRICTED
    assert projected.tokens[0].text is None
    assert projected.tokens[0].alternatives == ()
    assert projected.speeches[0].access_class is AccessClass.RESTRICTED
    assert projected.speeches[0].text is None
    assert projected.tables[0].access_class is AccessClass.RESTRICTED
    assert projected.embeddings[0].access_class is AccessClass.RESTRICTED
    assert projected.embeddings[0].values == ()
    assert projected.assertions[0].access_class is AccessClass.RESTRICTED
    assert projected.assertions[0].object_text is None
    for writer, suffix in (
        (write_json, "json"),
        (write_jsonl, "jsonl"),
        (write_jsonld, "jsonld"),
        (write_markdown, "md"),
        (write_rdf, "ttl"),
    ):
        output = writer(projected, tmp_path / f"public.{suffix}")
        assert "Hello" not in output.read_text(encoding="utf-8")


def test_public_projection_closes_restrictions_over_assertion_embedding_chains() -> None:
    payload = _bundle().model_dump(mode="python")
    payload["assertions"] = (
        *payload["assertions"],
        ArchiveAssertion(
            assertion_id="assertion-restricted",
            subject_id="speech-1",
            predicate="restricted",
            access_class=AccessClass.RESTRICTED,
        ).model_dump(mode="python"),
        ArchiveAssertion(
            assertion_id="assertion-via-embedding",
            subject_id="embedding-via-assertion",
            predicate="derived-from",
            object_text="restricted assertion derivative",
        ).model_dump(mode="python"),
        ArchiveAssertion(
            assertion_id="assertion-public-object",
            subject_id="speech-1",
            predicate="references",
            object_id="assertion-1",
            object_text="public reference",
        ).model_dump(mode="python"),
    )
    payload["embeddings"] = (
        *payload["embeddings"],
        ArchiveEmbedding(
            embedding_id="embedding-via-assertion",
            target_id="assertion-restricted",
            model_id="model-1",
            vector_dim=1,
            values=(0.5,),
        ).model_dump(mode="python"),
        ArchiveEmbedding(
            embedding_id="embedding-via-derived-assertion",
            target_id="assertion-via-embedding",
            model_id="model-1",
            vector_dim=1,
            values=(0.6,),
        ).model_dump(mode="python"),
    )

    projected = ArchiveBundle.model_validate(payload).public_projection()

    assertions = {item.assertion_id: item for item in projected.assertions}
    embeddings = {item.embedding_id: item for item in projected.embeddings}
    assert assertions["assertion-via-embedding"].access_class is AccessClass.RESTRICTED
    assert assertions["assertion-via-embedding"].object_text is None
    assert embeddings["embedding-via-assertion"].access_class is AccessClass.RESTRICTED
    assert embeddings["embedding-via-assertion"].values == ()
    assert embeddings["embedding-via-derived-assertion"].access_class is AccessClass.RESTRICTED
    assert embeddings["embedding-via-derived-assertion"].values == ()
    public_object = next(item for item in projected.assertions if item.assertion_id == "assertion-public-object")
    assert public_object.access_class is AccessClass.PUBLIC
    assert public_object.object_text == "public reference"


def test_public_projection_keeps_overlapping_restriction_sets_monotonic() -> None:
    payload = _bundle().model_dump(mode="python")
    payload["speeches"][0]["access_class"] = AccessClass.RESTRICTED
    payload["embeddings"][0]["embedding_id"] = "speech-1"
    payload["embeddings"] = (
        *payload["embeddings"],
        ArchiveEmbedding(
            embedding_id="descendant-embedding",
            target_id="speech-1",
            model_id="model-1",
            vector_dim=1,
            values=(0.7,),
        ).model_dump(mode="python"),
    )
    projected = ArchiveBundle.model_validate(payload).public_projection()
    descendant = next(item for item in projected.embeddings if item.embedding_id == "descendant-embedding")
    assert descendant.access_class is AccessClass.RESTRICTED
    assert descendant.values == ()


def test_public_serializers_reject_mixed_access_canary(tmp_path: Path) -> None:
    canary = "RESTRICTED_ARCHIVE_CANARY"
    raw = _bundle().model_dump(mode="json")
    raw["spans"][0]["text"] = canary
    raw["lines"][0]["text"] = canary
    raw["tokens"][0].update({"text": canary, "access_class": "restricted"})
    raw["speeches"][0]["text"] = canary
    raw["assertions"][0].update({"object_id": "speech-1", "object_text": canary})
    raw["embeddings"][0]["values"] = [0.314159, 0.271828]
    bundle = ArchiveBundle.model_validate(raw)

    for writer, filename in (
        (write_json, "archive.json"),
        (write_jsonl, "archive.jsonl"),
        (write_jsonld, "archive.jsonld"),
        (write_markdown, "archive.md"),
        (write_parquet, "archive.parquet"),
        (write_rdf, "archive.ttl"),
    ):
        output = writer(bundle, tmp_path / filename)
        assert canary not in output.read_bytes().decode("utf-8", errors="ignore"), filename


def test_serializers_are_deterministic_and_round_trip(tmp_path: Path) -> None:
    bundle = _bundle()
    json_path = write_json(bundle, tmp_path / "archive.json")
    jsonl_path = write_jsonl(bundle, tmp_path / "archive.jsonl")
    jsonld_path = write_jsonld(bundle, tmp_path / "archive.jsonld")
    md_path = write_markdown(bundle, tmp_path / "archive.md")
    parquet_path = write_parquet(bundle, tmp_path / "archive.parquet")
    rdf_path = write_rdf(bundle, tmp_path / "archive.ttl")

    assert ArchiveBundle.model_validate_json(json_path.read_text(encoding="utf-8")) == bundle
    assert len(jsonl_path.read_text(encoding="utf-8").splitlines()) == 13
    assert "@graph" in jsonld_path.read_text(encoding="utf-8")
    assert "Archive Bundle" in md_path.read_text(encoding="utf-8")
    assert parquet_path.stat().st_size > 0
    assert "@prefix" in rdf_path.read_text(encoding="utf-8")
    assert json.loads(json_path.read_text(encoding="utf-8"))["schema_version"] == "1.0.0"


def test_migration_is_explicit_and_versioned() -> None:
    legacy = _bundle().model_dump(mode="json")
    legacy["schema_version"] = "0.9.0"

    migrated = migrate_bundle(legacy)

    assert migrated.schema_version == "1.0.0"
    with pytest.raises(ValueError, match="unsupported source"):
        migrate_bundle({"schema_version": "2.0.0"})
