# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "spacy>=3.7.0",
#     "beautifulsoup4>=4.12.0",
#     "lxml>=5.1.0",
#     "msgspec>=0.18.0",
# ]
# ///

"""
Universal Legislative and Parliamentary NLP Abstraction Framework - Version 3.
Implements displaCy visualization exports and nested SpanGroup modeling
to support overlapping legislative citations.
"""

import json
import re
import typing as ty
from abc import ABC, abstractmethod
from pathlib import Path

import msgspec
import spacy
from bs4 import BeautifulSoup
from spacy import displacy
from spacy.language import Language
from spacy.tokens import Doc, Span

# ---------------------------------------------------------------------------
# 1. Configuration Abstraction
# ---------------------------------------------------------------------------


class FrameworkConfig(msgspec.Struct):
    """Configuration variables mapping regional and schema target properties."""

    country: str
    jurisdiction: str
    source_data_format: str  # Options: 'XML' | 'HTML' | 'JSONL'
    target_schema_standard: str  # Options: 'ParlaMint-TEI-Ana' | 'Akoma-Ntoso' | 'ParlaCAP-JSONL'
    base_spacy_pipeline: str = "en_core_web_sm"


# ---------------------------------------------------------------------------
# 2. Universal Ingestion Engine
# ---------------------------------------------------------------------------


class DocumentChunk(msgspec.Struct):
    """Internal standardized text block with metadata mapped from ingestion."""

    chunk_id: str
    text: str
    structural_type: str  # e.g., 'section', 'speech', 'clause'
    attributes: dict[str, str] = {}


class UniversalIngestionEngine(ABC):
    """Abstract Base Class for format-specific ingestion engines."""

    @abstractmethod
    def ingest(self, raw_data: str) -> list[DocumentChunk]:
        pass


class XMLIngestionEngine(UniversalIngestionEngine):
    """Ingests and parses XML trees (e.g., PCO legislative XML)."""

    def ingest(self, raw_data: str) -> list[DocumentChunk]:
        soup = BeautifulSoup(raw_data, "xml")
        chunks = []
        for node in soup.find_all(["section", "speech", "part"]):
            node_id = node.get("id", f"xml-chunk-{len(chunks)}")
            structural_type = node.name
            text_content = node.get_text(separator=" ").strip()
            attrs = {k: v for k, v in node.attrs.items() if k != "id"}
            chunks.append(
                DocumentChunk(
                    chunk_id=node_id,
                    text=text_content,
                    structural_type=structural_type,
                    attributes=attrs,
                )
            )
        return chunks


class HTMLIngestionEngine(UniversalIngestionEngine):
    """Ingests and parses HTML layouts."""

    def ingest(self, raw_data: str) -> list[DocumentChunk]:
        soup = BeautifulSoup(raw_data, "html.parser")
        chunks = []
        for node in soup.find_all(["article", "div", "p"]):
            if "id" in node.attrs:
                node_id = node["id"]
                structural_type = node.name
                text_content = node.get_text(separator=" ").strip()
                chunks.append(
                    DocumentChunk(
                        chunk_id=node_id,
                        text=text_content,
                        structural_type=structural_type,
                        attributes={},
                    )
                )
        return chunks


class JSONLIngestionEngine(UniversalIngestionEngine):
    """Ingests and parses JSON-Lines serialized strings."""

    def ingest(self, raw_data: str) -> list[DocumentChunk]:
        chunks = []
        for idx, line in enumerate(raw_data.strip().split("\n")):
            if not line.strip():
                continue
            data = json.loads(line)
            node_id = data.get("id", f"jsonl-chunk-{idx}")
            text_content = data.get("text", "")
            structural_type = data.get("type", "paragraph")
            chunks.append(
                DocumentChunk(
                    chunk_id=node_id,
                    text=text_content,
                    structural_type=structural_type,
                    attributes=data.get("metadata", {}),
                )
            )
        return chunks


def get_ingestion_engine(data_format: str) -> UniversalIngestionEngine:
    if data_format.upper() == "XML":
        return XMLIngestionEngine()
    if data_format.upper() == "HTML":
        return HTMLIngestionEngine()
    if data_format.upper() == "JSONL":
        return JSONLIngestionEngine()
    raise ValueError(f"Unsupported source format: {data_format}")


# ---------------------------------------------------------------------------
# 3. Dynamic Metadata Extension Registry
# ---------------------------------------------------------------------------


class MetaExtensionRegistry:
    """Manages dynamic naming and registration of custom spaCy extensions."""

    @staticmethod
    def sanitize_name(name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_]", "_", name).lower()

    @classmethod
    def register(cls, config: FrameworkConfig) -> tuple[str, str, str]:
        namespace = cls.sanitize_name(f"{config.country}_{config.target_schema_standard}")
        country_key = f"{namespace}_country"
        schema_key = f"{namespace}_structural_type"
        chunk_id_key = f"{namespace}_chunk_id"

        if not Doc.has_extension(country_key):
            Doc.set_extension(country_key, default=config.country)
        if not Span.has_extension(schema_key):
            Span.set_extension(schema_key, default=None)
        if not Span.has_extension(chunk_id_key):
            Span.set_extension(chunk_id_key, default=None)

        return country_key, schema_key, chunk_id_key


# ---------------------------------------------------------------------------
# 4. Modular spaCy Bridge & Nested SpanGroup Component (SOTA)
# ---------------------------------------------------------------------------


@Language.factory("universal_metadata_bridge_v3")
def create_metadata_bridge_v3(
    nlp: Language, name: str, country_key: str, schema_key: str, chunk_id_key: str
) -> ty.Callable[[Doc], Doc]:
    return ModularSpaCyBridgeComponentV3(nlp, name, country_key, schema_key, chunk_id_key)


class ModularSpaCyBridgeComponentV3:
    """Maps document metadata and scaffolds overlapping Spans via SpanGroups."""

    def __init__(
        self, nlp: Language, name: str, country_key: str, schema_key: str, chunk_id_key: str
    ):
        self._nlp = nlp
        self.name = name
        self.country_key = country_key
        self.schema_key = schema_key
        self.chunk_id_key = chunk_id_key

    def __call__(self, doc: Doc) -> Doc:
        if doc.has_extension("chunk_metadata") and doc._.chunk_metadata:
            meta = doc._.chunk_metadata
            full_span = doc[0 : len(doc)]
            full_span._.set(self.schema_key, meta.get("structural_type"))
            full_span._.set(self.chunk_id_key, meta.get("chunk_id"))

            # Map structural node as a Span inside doc.spans SpanGroup
            # Unlike doc.ents, SpanGroups support overlapping and nested boundaries
            span_group_name = "nz_nested_entities"
            if span_group_name not in doc.spans:
                doc.spans[span_group_name] = []

            doc.spans[span_group_name].append(full_span)
        return doc


if not Doc.has_extension("chunk_metadata"):
    Doc.set_extension("chunk_metadata", default=None)


# ---------------------------------------------------------------------------
# 5. SOTA Target Schema Emitter (Maximal Standards Use)
# ---------------------------------------------------------------------------


class TargetSchemaEmitter:
    """Enriches output configurations to comply strictly with international schemas."""

    def __init__(
        self, config: FrameworkConfig, country_key: str, schema_key: str, chunk_id_key: str
    ):
        self.config = config
        self.country_key = country_key
        self.schema_key = schema_key
        self.chunk_id_key = chunk_id_key

    def emit(self, doc: Doc) -> str:
        standard = self.config.target_schema_standard.upper()
        full_span = doc[0 : len(doc)]
        structural_type = full_span._.get(self.schema_key)
        chunk_id = full_span._.get(self.chunk_id_key)

        if "PARLAMINT" in standard:
            return self._emit_parlamint_tei(doc, chunk_id, structural_type)
        if "AKOMA" in standard:
            return self._emit_akoma_ntoso(doc, chunk_id, structural_type)
        if "PARLACAP" in standard:
            return self._emit_parlacap_jsonl(doc, chunk_id, structural_type)
        raise ValueError(f"Unknown target schema: {self.config.target_schema_standard}")

    def _emit_parlamint_tei(self, doc: Doc, chunk_id: str, struct_type: str) -> str:
        """Serializes to ParlaMint-TEI-Ana with sentence tags and Morphosyntactic (MSD) features."""
        lines = []
        speaker_id = "unknown_speaker"
        lines.append(f'<u xml:id="{chunk_id}" who="#{speaker_id}" ana="#{struct_type}">')
        for s_idx, sent in enumerate(doc.sents):
            lines.append(f'  <s xml:id="{chunk_id}.s{s_idx}">')
            for token in sent:
                if token.is_space:
                    continue
                msd = f"UPosTag={token.pos_}|Tag={token.tag_}"
                if token.ent_type_:
                    lines.append(f'    <name type="{token.ent_type_}">')
                    lines.append(
                        f'      <w lemma="{token.lemma_}" pos="{token.pos_}" msd="{msd}">{token.text}</w>'
                    )
                    lines.append("    </name>")
                else:
                    lines.append(
                        f'    <w lemma="{token.lemma_}" pos="{token.pos_}" msd="{msd}">{token.text}</w>'
                    )
            lines.append("  </s>")
        lines.append("</u>")
        return "\n".join(lines)

    def _emit_akoma_ntoso(self, doc: Doc, chunk_id: str, struct_type: str) -> str:
        """Serializes into complete Akoma-Ntoso XML layout with Identification Metadata blocks."""
        lines = []
        lines.append("<akomaNtoso>")
        lines.append(f'  <{struct_type} id="{chunk_id}">')
        lines.append("    <meta>")
        lines.append('      <identification source="#nlp_policy_nz">')
        lines.append("        <FRBRWork>")
        lines.append(
            f'          <FRBRthis value="/{self.config.country}/{struct_type}/{chunk_id}/main"/>'
        )
        lines.append(
            f'          <FRBRuri value="/{self.config.country}/{struct_type}/{chunk_id}"/>'
        )
        lines.append("        </FRBRWork>")
        lines.append("      </identification>")
        lines.append("    </meta>")
        lines.append("    <body>")
        lines.append("      <mainBody>")
        lines.append("        <content>")
        lines.append(f"          <p>{doc.text}</p>")
        lines.append("        </content>")
        lines.append("      </mainBody>")
        lines.append("    </body>")
        lines.append(f"  </{struct_type}>")
        lines.append("</akomaNtoso>")
        return "\n".join(lines)

    def _emit_parlacap_jsonl(self, doc: Doc, chunk_id: str, struct_type: str) -> str:
        """Serializes to ParlaCAP-JSONL containing joint syntax-aware token mappings."""
        tokens = []
        for t in doc:
            if t.is_space:
                continue
            tokens.append(
                {
                    "text": t.text,
                    "lemma": t.lemma_,
                    "pos": t.pos_,
                    "ner": t.ent_type_,
                    "deprel": t.dep_,
                    "head_index": t.head.i,
                }
            )
        data = {
            "id": chunk_id,
            "country": self.config.country,
            "structural_type": struct_type,
            "tokens": tokens,
        }
        return json.dumps(data)


# ---------------------------------------------------------------------------
# 6. SOTA Annotation Visualizer (displaCy Bridge)
# ---------------------------------------------------------------------------


class SOTAPipelineVisualizer:
    """Exports clean, styled HTML markup of document annotations via displaCy."""

    @staticmethod
    def generate_html_report(doc: Doc, output_path: str | None = None) -> str:
        """Generates static HTML string rendering sentence boundaries and entity tags."""
        colors = {
            "LAW": "linear-gradient(90deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%)",
            "SECTION": "linear-gradient(90deg, #a1c4fd 0%, #c2e9fb 100%)",
            "PRELIM": "linear-gradient(90deg, #fdfcfb 0%, #e2d1c3 100%)",
        }
        options = {"colors": colors}

        # We temporarily copy SpanGroups into doc.ents to display them inside displaCy
        # as displaCy focuses on doc.ents for rendering structural highlighting.
        spans = doc.spans.get("nz_nested_entities", [])
        original_ents = doc.ents

        ents_to_set = []
        for span in spans:
            struct_type = span._.get("nz_legislation_parlamint_tei_ana_structural_type") or "PRELIM"
            ents_to_set.append(Span(doc, span.start, span.end, label=struct_type.upper()))

        doc.ents = spacy.util.filter_spans(ents_to_set)

        # Render HTML using displaCy
        html = displacy.render(doc, style="ent", options=options, page=True, jupyter=False)

        # Restore original ents
        doc.ents = original_ents

        if output_path:
            Path(output_path).write_text(html, encoding="utf-8")

        return html


# ---------------------------------------------------------------------------
# 7. Pipeline Controller and Switcher Demo
# ---------------------------------------------------------------------------

SAMPLE_XML = (
    '<section id="sec-5" title="Interpretation"><para>The terms apply to this Act.</para></section>'
)


def run_framework(config: FrameworkConfig, raw_data: str) -> Doc:
    engine = get_ingestion_engine(config.source_data_format)
    chunks = engine.ingest(raw_data)

    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)

    nlp = spacy.blank("en")
    nlp.add_pipe(
        "universal_metadata_bridge_v3",
        config={"country_key": country_key, "schema_key": schema_key, "chunk_id_key": chunk_id_key},
    )
    nlp.add_pipe("sentencizer")

    # For demo, process the first chunk
    chunk = chunks[0]
    doc = nlp.make_doc(chunk.text)
    doc._.chunk_metadata = {"chunk_id": chunk.chunk_id, "structural_type": chunk.structural_type}
    return nlp(doc)


def run_demo() -> None:
    config_nz = FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    doc = run_framework(config_nz, SAMPLE_XML)

    for _group_name, spans in doc.spans.items():
        for _span in spans:
            pass

    # Generates static HTML displaying our highlighted entities
    SOTAPipelineVisualizer.generate_html_report(doc, "conductor/annotation_report.html")


if __name__ == "__main__":
    run_demo()
