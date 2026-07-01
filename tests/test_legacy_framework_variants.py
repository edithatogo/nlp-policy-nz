from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest
import spacy
from bs4 import BeautifulSoup as RealBeautifulSoup

if TYPE_CHECKING:
    from types import ModuleType

REAL_SPACY_BLANK = spacy.blank


LEGACY_MODULES = [
    (
        "legacy_universal_framework",
        Path("src/nlp_policy_nz/universal_framework.py"),
        '<div type="section" xml:id="sec-5">',
    ),
    (
        "legacy_universal_framework_v1",
        Path("src/nlp_policy_nz/universal_framework_v1.py"),
        '<div type="section" xml:id="sec-5">',
    ),
    (
        "legacy_universal_framework_v2",
        Path("src/nlp_policy_nz/universal_framework_v2.py"),
        '<u xml:id="sec-5"',
    ),
]


class _PatchedPipeline:
    def __init__(self, module: ModuleType) -> None:
        self._module = module
        self._nlp = REAL_SPACY_BLANK("en")
        if not self._nlp.has_pipe("sentencizer"):
            self._nlp.add_pipe("sentencizer")
        self._bridge = None

    def add_pipe(self, name: str, config: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        if name.startswith("universal_metadata_bridge"):
            bridge_args = config or {}
            bridge_cls = getattr(self._module, "ModularSpaCyBridgeComponent", None)
            if bridge_cls is None:
                bridge_cls = self._module.ModularSpaCyBridgeComponentV2
            self._bridge = bridge_cls(
                self._nlp,
                name,
                bridge_args["country_key"],
                bridge_args["schema_key"],
                bridge_args["chunk_id_key"],
            )
            return self._bridge
        if name == "sentencizer":
            return None
        raise AssertionError(f"Unexpected pipeline component: {name}")

    def make_doc(self, text: str) -> Any:
        return self._nlp.make_doc(text)

    def __call__(self, doc: Any) -> Any:
        doc = self._nlp(doc)
        if self._bridge is not None:
            doc = self._bridge(doc)
        return doc


def _load_module(module_name: str, path: Path) -> ModuleType:
    with (
        patch.object(
            spacy.language.Language,
            "factory",
            new=lambda *args, **kwargs: lambda func: func,
        ),
    ):
        spec = importlib.util.spec_from_file_location(module_name, path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def _html_fallback_soup(markup: str, _features: str | None = None) -> RealBeautifulSoup:
    return RealBeautifulSoup(markup, "html.parser")


def _seed_span_metadata(doc: Any, schema_key: str, chunk_id_key: str, chunk: Any) -> None:
    span = doc[0 : len(doc)]
    span._.set(schema_key, chunk.structural_type)
    span._.set(chunk_id_key, chunk.chunk_id)


@pytest.mark.parametrize(("module_name", "path", "tei_marker"), LEGACY_MODULES)
def test_legacy_framework_variants_cover_ingestion_and_emission(
    module_name: str, path: Path, tei_marker: str
) -> None:
    module = _load_module(module_name, path)
    sample_xml = (
        '<section id="sec-5" title="Interpretation"><para>The terms apply.</para></section>'
    )
    sample_html = '<article id="art-1"><p>Article text.</p></article>'
    sample_jsonl = (
        '{"id": "speech-102", "text": "I support this amendment.", '
        '"type": "speech", "metadata": {"speaker": "MP Jones"}}'
    )

    config_xml = module.FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    config_html = module.FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="HTML",
        target_schema_standard="Akoma-Ntoso",
    )
    config_jsonl = module.FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="JSONL",
        target_schema_standard="ParlaCAP-JSONL",
    )

    assert module.MetaExtensionRegistry.sanitize_name("New Zealand Catala-DSL") == (
        "new_zealand_catala_dsl"
    )

    with patch.object(module, "BeautifulSoup", new=_html_fallback_soup):
        xml_engine = module.get_ingestion_engine("XML")
        html_engine = module.get_ingestion_engine("HTML")
        jsonl_engine = module.get_ingestion_engine("JSONL")
        assert xml_engine.ingest(sample_xml)[0].chunk_id == "sec-5"
        assert html_engine.ingest(sample_html)[0].chunk_id == "art-1"
        assert jsonl_engine.ingest(sample_jsonl)[0].chunk_id == "speech-102"

        country_key, schema_key, chunk_id_key = module.MetaExtensionRegistry.register(config_xml)
        pipeline = _PatchedPipeline(module)
        emitter = module.TargetSchemaEmitter(config_xml, country_key, schema_key, chunk_id_key)

        xml_chunk = xml_engine.ingest(sample_xml)[0]
        xml_doc = pipeline.make_doc(xml_chunk.text)
        xml_doc._.chunk_metadata = {
            "chunk_id": xml_chunk.chunk_id,
            "structural_type": xml_chunk.structural_type,
        }
        xml_doc = pipeline(xml_doc)
        _seed_span_metadata(xml_doc, schema_key, chunk_id_key, xml_chunk)
        xml_output = emitter.emit(xml_doc)
        assert tei_marker in xml_output

        html_chunk = html_engine.ingest(sample_html)[0]
        html_doc = pipeline.make_doc(html_chunk.text)
        html_doc._.chunk_metadata = {
            "chunk_id": html_chunk.chunk_id,
            "structural_type": html_chunk.structural_type,
        }
        html_doc = pipeline(html_doc)
        _seed_span_metadata(html_doc, schema_key, chunk_id_key, html_chunk)
        html_output = module.TargetSchemaEmitter(
            config_html, country_key, schema_key, chunk_id_key
        ).emit(html_doc)
        assert "<akomaNtoso>" in html_output
        assert 'id="art-1"' in html_output

        jsonl_chunk = jsonl_engine.ingest(sample_jsonl)[0]
        jsonl_doc = pipeline.make_doc(jsonl_chunk.text)
        jsonl_doc._.chunk_metadata = {
            "chunk_id": jsonl_chunk.chunk_id,
            "structural_type": jsonl_chunk.structural_type,
        }
        jsonl_doc = pipeline(jsonl_doc)
        _seed_span_metadata(jsonl_doc, schema_key, chunk_id_key, jsonl_chunk)
        jsonl_output = module.TargetSchemaEmitter(
            config_jsonl, country_key, schema_key, chunk_id_key
        ).emit(jsonl_doc)
        parsed_jsonl = json.loads(jsonl_output)
        assert parsed_jsonl["country"] == "New Zealand"
        assert parsed_jsonl["structural_type"] == "speech"
        assert parsed_jsonl["id"] == "speech-102"

        with patch.object(module.spacy, "blank", new=lambda _lang: _PatchedPipeline(module)):
            module.run_demo()


def test_xml_parser_round_trip_and_cross_references() -> None:
    from nlp_policy_nz import xml_parser as module

    with patch.object(module, "BeautifulSoup", new=_html_fallback_soup):
        parser = module.LegislativeXMLParser(module.SAMPLE_NZ_XML)
        clean_text, metadata = parser.parse()

        assert "Purpose" in clean_text
        assert metadata
        assert metadata[0].element_type in {"act", "part", "section", "heading", "para"}

        nlp = spacy.blank("en")
        nlp.add_pipe("sentencizer")
        doc = nlp.make_doc(clean_text)
        doc._.nz_xml_metadata = metadata
        doc = module.nz_xml_structure_injector(doc)
        doc = module.nz_cross_reference_matcher(doc)

        assert doc.spans["nz_xml_structure"]
        assert any(span._.nz_element_type for span in doc.spans["nz_xml_structure"])
        assert doc.spans["nz_cross_references"]

        module.run_demo()
