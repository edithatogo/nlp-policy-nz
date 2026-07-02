from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from nlp_policy_nz import get_ingestion_engine, unstructured_ingestion as module


@dataclass
class _Metadata:
    element_id: str
    page_number: int
    filetype: str
    coordinates: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "element_id": self.element_id,
            "page_number": self.page_number,
            "filetype": self.filetype,
            "coordinates": self.coordinates,
        }


@dataclass
class _Element:
    text: str
    category: str
    metadata: _Metadata


def test_unstructured_ingestion_partitions_local_file(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "sample.docx"
    source.write_text("placeholder", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_partition(**kwargs: object) -> list[_Element]:
        captured.update(kwargs)
        return [
            _Element(
                text="Heading text",
                category="Title",
                metadata=_Metadata(
                    element_id="heading-1",
                    page_number=2,
                    filetype="docx",
                    coordinates={"x": 1, "y": 2},
                ),
            )
        ]

    monkeypatch.setattr(module, "_partition_document", fake_partition)

    engine = module.UnstructuredIngestionEngine(strategy="fast")
    chunks = engine.ingest_file(source)

    assert captured["filename"] == str(source)
    assert captured["strategy"] == "fast"
    assert len(chunks) == 1

    chunk = chunks[0]
    assert chunk.chunk_id == "heading-1"
    assert chunk.text == "Heading text"
    assert chunk.structural_type == "Title"
    assert chunk.attributes["source_path"] == str(source)
    assert chunk.attributes["adapter"] == "unstructured"
    assert chunk.attributes["partition_strategy"] == "fast"
    assert chunk.attributes["quality_flags"] == '["unstructured", "text_present", "page:2", "filetype:docx", "layout"]'


def test_unstructured_ingestion_raises_without_dependency(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "missing.pdf"
    source.write_text("placeholder", encoding="utf-8")

    monkeypatch.setattr(module, "_partition_document", None)

    engine = module.UnstructuredIngestionEngine()

    with pytest.raises(ImportError, match="optional 'unstructured' extra"):
        engine.ingest_file(source)


def test_unstructured_ingestion_reports_missing_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(module, "_partition_document", SimpleNamespace())

    engine = module.UnstructuredIngestionEngine()

    with pytest.raises(FileNotFoundError, match="expects an existing local file"):
        engine.ingest_file(tmp_path / "absent.docx")


def test_ingestion_factory_exposes_unstructured_engine() -> None:
    engine = get_ingestion_engine("UNSTRUCTURED")

    assert isinstance(engine, module.UnstructuredIngestionEngine)


def test_unstructured_compares_against_canonical_html_parser(
    monkeypatch, tmp_path: Path
) -> None:
    source = tmp_path / "sample.html"
    source.write_text(
        "<article id='a'>Alpha</article><p id='b'>Beta</p>",
        encoding="utf-8",
    )

    def fake_partition(**kwargs: object) -> list[_Element]:
        assert kwargs["filename"] == str(source)
        return [
            _Element(
                text="Alpha",
                category="Title",
                metadata=_Metadata(
                    element_id="a",
                    page_number=1,
                    filetype="html",
                    coordinates={"x": 1, "y": 2},
                ),
            ),
            _Element(
                text="Beta",
                category="NarrativeText",
                metadata=_Metadata(
                    element_id="b",
                    page_number=1,
                    filetype="html",
                    coordinates={"x": 3, "y": 4},
                ),
            ),
        ]

    monkeypatch.setattr(module, "_partition_document", fake_partition)

    evaluation = module.compare_with_html_parser(source)

    assert evaluation["adapter_chunk_count"] == 2
    assert evaluation["canonical_chunk_count"] == 2
    assert evaluation["shared_chunk_ids"] == ["a", "b"]
    assert evaluation["adapter_only_chunk_ids"] == []
    assert evaluation["canonical_only_chunk_ids"] == []
