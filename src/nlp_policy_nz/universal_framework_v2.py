# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "spacy>=3.7.0",
#     "beautifulsoup4>=4.12.0",
#     "lxml>=5.1.0",
#     "msgspec>=0.18.0",
# ]
# ///

"""Universal Legislative and Parliamentary NLP Abstraction Framework - Version 2.

Enforces maximal use of ParlaMint-TEI-Ana, Akoma-Ntoso, and ParlaCAP-JSONL schemas.
"""

import json
import re
import typing as ty
from abc import ABC, abstractmethod

import msgspec
import spacy
from bs4 import BeautifulSoup
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
        """Ingests raw text and extracts standardized DocumentChunks."""


class XMLIngestionEngine(UniversalIngestionEngine):
    """Ingests and parses XML trees (e.g., PCO legislative XML)."""

    def ingest(self, raw_data: str) -> list[DocumentChunk]:
        """Ingest raw data into document chunks."""
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
        """Ingest raw data into document chunks."""
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
        """Ingest raw data into document chunks."""
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
    """Return the ingestion engine for the data format."""
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
        """Return a safe extension name."""
        return re.sub(r"[^a-zA-Z0-9_]", "_", name).lower()

    @classmethod
    def register(cls, config: FrameworkConfig) -> tuple[str, str, str]:
        """Register metadata extensions for the configuration."""
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
# 4. Modular spaCy Bridge Component
# ---------------------------------------------------------------------------


@Language.factory("universal_metadata_bridge_v2")
def create_metadata_bridge_v2(
    nlp: Language, name: str, country_key: str, schema_key: str, chunk_id_key: str
) -> ty.Callable[[Doc], Doc]:
    """Create the metadata bridge component."""
    return ModularSpaCyBridgeComponentV2(nlp, name, country_key, schema_key, chunk_id_key)


class ModularSpaCyBridgeComponentV2:
    """Custom spaCy component mapping schema metadata properties onto Spans."""

    def __init__(
        self, nlp: Language, name: str, country_key: str, schema_key: str, chunk_id_key: str
    ) -> None:
        """Initialize the instance."""
        self._nlp = nlp
        self.name = name
        self._nlp = nlp
        self.country_key = country_key
        self.schema_key = schema_key
        self.chunk_id_key = chunk_id_key

    def __call__(self, doc: Doc) -> Doc:
        """Process and return the document."""
        if doc.has_extension("chunk_metadata") and doc._.chunk_metadata:
            meta = doc._.chunk_metadata
            full_span = doc[0 : len(doc)]
            full_span._.set(self.schema_key, meta.get("structural_type"))
            full_span._.set(self.chunk_id_key, meta.get("chunk_id"))
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
    ) -> None:
        """Initialize the instance."""
        self.config = config
        self.country_key = country_key
        self.schema_key = schema_key
        self.chunk_id_key = chunk_id_key

    def emit(self, doc: Doc) -> str:
        """Emit the document in the configured target schema."""
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
        """Serialize to ParlaMint-TEI-Ana with sentence tags and Morphosyntactic features."""
        lines = []
        speaker_id = "unknown_speaker"

        # UTTERANCE wrapper for parliamentary speeches
        lines.append(f'<u xml:id="{chunk_id}" who="#{speaker_id}" ana="#{struct_type}">')

        # Group tokens into sentences (<s>) using spaCy sentencizer
        for s_idx, sent in enumerate(doc.sents):
            lines.append(f'  <s xml:id="{chunk_id}.s{s_idx}">')
            for token in sent:
                if token.is_space:
                    continue
                # Compile detailed MSD features using tag_
                msd = f"UPosTag={token.pos_}|Tag={token.tag_}"

                # Check for named entities to nest inside <name>
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
        """Serialize into complete Akoma-Ntoso XML layout with identification metadata blocks."""
        lines = []
        lines.append("<akomaNtoso>")
        lines.append(f'  <{struct_type} id="{chunk_id}">')

        # Meta identification block
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

        # Content body
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
        """Serialize to ParlaCAP-JSONL containing joint syntax-aware token mappings."""
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
# 6. Pipeline Controller and Switcher Demo
# ---------------------------------------------------------------------------

SAMPLE_XML = (
    '<section id="sec-5" title="Interpretation"><para>The terms apply to this Act.</para></section>'
)
SAMPLE_JSONL = '{"id": "speech-102", "text": "I support this amendment for the region.", "type": "speech", "metadata": {"speaker": "MP Jones"}}'


def run_framework(config: FrameworkConfig, raw_data: str) -> str:
    """Run the configured framework over raw data."""
    engine = get_ingestion_engine(config.source_data_format)
    chunks = engine.ingest(raw_data)

    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)

    # Initialize blank model
    nlp = spacy.blank("en")
    nlp.add_pipe(
        "universal_metadata_bridge_v2",
        config={"country_key": country_key, "schema_key": schema_key, "chunk_id_key": chunk_id_key},
    )
    nlp.add_pipe("sentencizer")

    emitter = TargetSchemaEmitter(config, country_key, schema_key, chunk_id_key)
    output_lines = []

    for chunk in chunks:
        doc = nlp.make_doc(chunk.text)
        doc._.chunk_metadata = {
            "chunk_id": chunk.chunk_id,
            "structural_type": chunk.structural_type,
        }
        doc = nlp(doc)
        serialized = emitter.emit(doc)
        output_lines.append(serialized)

    return "\n\n".join(output_lines)


def run_demo() -> None:
    # Scenario A: New Zealand statute XML targeting ParlaMint-TEI-Ana
    """Run the demonstration pipeline."""
    config_nz = FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    run_framework(config_nz, SAMPLE_XML)

    # Scenario B: Switch parameters dynamically to UK JSONL data targeting ParlaCAP-JSONL
    config_uk = FrameworkConfig(
        country="United Kingdom",
        jurisdiction="UK Hansard Parliamentary Debates",
        source_data_format="JSONL",
        target_schema_standard="ParlaCAP-JSONL",
    )
    run_framework(config_uk, SAMPLE_JSONL)


if __name__ == "__main__":
    run_demo()
