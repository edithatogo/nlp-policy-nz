# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "spacy>=3.7.0",
#     "beautifulsoup4>=4.12.0",
#     "lxml>=5.1.0",
#     "msgspec>=0.18.0",
# ]
# ///

"""Universal Legislative and Parliamentary NLP Abstraction Framework - Version 3.

Implements displaCy visualization exports and nested SpanGroup modeling
to support overlapping legislative citations.
"""

# pyright: reportUntypedFunctionDecorator=false

import json
import re
import typing as ty
from abc import ABC, abstractmethod
from pathlib import Path
from xml.etree import ElementTree as ET

import msgspec
import spacy
from bs4 import BeautifulSoup, Tag
from spacy import displacy
from spacy.language import Language
from spacy.tokens import Doc, Span


class _ModalityValue(ty.Protocol):
    """Minimal modality value protocol used by emitters."""

    value: str


class _ModalityAnnotation(ty.Protocol):
    """Minimal modality annotation protocol used by emitters."""

    modality: _ModalityValue
    scope: str | None
    trigger: str


def _text_attr(value: object, fallback: str) -> str:
    """Return a BeautifulSoup or JSON attribute as text."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        raw_parts = ty.cast("list[object]", value)
        parts = [part for part in raw_parts if isinstance(part, str)]
        return " ".join(parts) if parts else fallback
    return fallback


def _string_mapping(value: object) -> dict[str, str]:
    """Return a dictionary containing only string keys and values."""
    if not isinstance(value, dict):
        return {}
    items = ty.cast("dict[object, object]", value).items()
    return {str(key): str(item) for key, item in items}


def _chunk_metadata(doc: Doc) -> dict[str, str] | None:
    """Return guarded chunk metadata from a dynamic spaCy extension."""
    if not doc.has_extension("chunk_metadata"):
        return None
    value = doc._.chunk_metadata
    metadata = _string_mapping(value)
    return metadata or None


def _span_extension_text(span: Span, key: str, fallback: str) -> str:
    """Return a guarded string value from a dynamic span extension."""
    value = span._.get(key)
    return value if isinstance(value, str) else fallback


def _modality_annotations(doc: Doc) -> list[_ModalityAnnotation]:
    """Return guarded modality annotations from dynamic spaCy state."""
    if doc.has_extension("modality_annotations"):
        value = doc._.get("modality_annotations")
        if isinstance(value, list):
            return ty.cast("list[_ModalityAnnotation]", value)
    return []


def _detect_modality_annotations(doc: Doc) -> list[_ModalityAnnotation]:
    """Detect modality annotations with a typed boundary around the detector."""
    from nlp_policy_nz.legal.modality import detect_modality

    temp_nlp = spacy.blank("en")
    return ty.cast("list[_ModalityAnnotation]", detect_modality(doc.text, temp_nlp))


def _span_group(doc: Doc, name: str) -> list[Span]:
    """Return a typed list of spans from a dynamic SpanGroup mapping."""
    groups = ty.cast("dict[str, object]", doc.spans)
    group = groups.get(name)
    if group is None:
        return []
    return list(ty.cast("ty.Iterable[Span]", group))

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
        """Ingest raw data into document chunks."""


class XMLIngestionEngine(UniversalIngestionEngine):
    """Ingests and parses XML trees (e.g., PCO legislative XML)."""

    def ingest(self, raw_data: str) -> list[DocumentChunk]:
        """Ingest raw data into document chunks."""
        try:
            root = ET.fromstring(raw_data)  # noqa: S314 - legacy demo parser keeps ElementTree compatibility.
        except ET.ParseError:
            root = None

        chunks: list[DocumentChunk] = []
        if root is not None:
            for node in root.iter():
                if node.tag not in {"section", "speech", "part"}:
                    continue
                node_id = str(node.attrib.get("id", f"xml-chunk-{len(chunks)}"))
                attrs: dict[str, str] = {str(k): str(v) for k, v in node.attrib.items() if k != "id"}
                text_content = " ".join(text.strip() for text in node.itertext() if text.strip())
                chunks.append(
                    DocumentChunk(
                        chunk_id=node_id,
                        text=text_content,
                        structural_type=str(node.tag),
                        attributes=attrs,
                    )
                )
            return chunks

        soup = BeautifulSoup(raw_data, "html.parser")
        for node in soup.find_all(["section", "speech", "part"]):
            if not isinstance(node, Tag):
                continue
            node_id = _text_attr(node.get("id"), f"xml-chunk-{len(chunks)}")
            structural_type = str(node.name or "section")
            text_content = node.get_text(separator=" ").strip()
            attrs = {str(k): _text_attr(v, "") for k, v in node.attrs.items() if k != "id"}
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
        chunks: list[DocumentChunk] = []
        for node in soup.find_all(["article", "div", "p"]):
            if not isinstance(node, Tag):
                continue
            if "id" in node.attrs:
                node_id = _text_attr(node.get("id"), f"html-chunk-{len(chunks)}")
                structural_type = str(node.name or "div")
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
        chunks: list[DocumentChunk] = []
        for idx, line in enumerate(raw_data.strip().split("\n")):
            if not line.strip():
                continue
            raw = json.loads(line)
            data: dict[str, object] = ty.cast("dict[str, object]", raw) if isinstance(raw, dict) else {}
            node_id = _text_attr(data.get("id"), f"jsonl-chunk-{idx}")
            text_content = _text_attr(data.get("text"), "")
            structural_type = _text_attr(data.get("type"), "paragraph")
            chunks.append(
                DocumentChunk(
                    chunk_id=node_id,
                    text=text_content,
                    structural_type=structural_type,
                    attributes=_string_mapping(data.get("metadata")),
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
# 4. Modular spaCy Bridge & Nested SpanGroup Component (SOTA)
# ---------------------------------------------------------------------------


@Language.factory("universal_metadata_bridge_v3")
def create_metadata_bridge_v3(
    nlp: Language, name: str, country_key: str, schema_key: str, chunk_id_key: str
) -> ty.Callable[[Doc], Doc]:
    """Create the metadata bridge component."""
    return ModularSpaCyBridgeComponentV3(nlp, name, country_key, schema_key, chunk_id_key)


class ModularSpaCyBridgeComponentV3:
    """Maps document metadata and scaffolds overlapping Spans via SpanGroups."""

    def __init__(
        self, nlp: Language, name: str, country_key: str, schema_key: str, chunk_id_key: str
    ) -> None:
        """Initialize the instance."""
        self._nlp = nlp
        self.name = name
        self.country_key = country_key
        self.schema_key = schema_key
        self.chunk_id_key = chunk_id_key

    def __call__(self, doc: Doc) -> Doc:
        """Process and return the document."""
        meta = _chunk_metadata(doc)
        if meta is not None:
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
        structural_type = _span_extension_text(full_span, self.schema_key, "section")
        chunk_id = _span_extension_text(full_span, self.chunk_id_key, "chunk-0")

        if "PARLAMINT" in standard:
            return self._emit_parlamint_tei(doc, chunk_id, structural_type)
        if "AKOMA" in standard:
            return self._emit_akoma_ntoso(doc, chunk_id, structural_type)
        if "PARLACAP" in standard:
            return self._emit_parlacap_jsonl(doc, chunk_id, structural_type)
        if "CATALA" in standard:
            return self._emit_catala_dsl(doc, chunk_id, structural_type)
        raise ValueError(f"Unknown target schema: {self.config.target_schema_standard}")

    def _emit_parlamint_tei(self, doc: Doc, chunk_id: str, struct_type: str) -> str:
        """Serialize to ParlaMint-TEI-Ana with sentence tags and Morphosyntactic features."""
        lines: list[str] = []
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
        """Serialize into complete Akoma-Ntoso XML layout with identification metadata blocks."""
        # Māori Language Guard Integration (Token-based lexical matching & macron detection)
        from nlp_policy_nz.guard.normalizer import is_macronized
        from nlp_policy_nz.guard.tokenizer_exceptions import TE_REO_LEXICAL_ATOM_SET

        processed_tokens: list[str] = []
        tikanga_ontology: dict[str, str] = {
            "kaitiakitanga": "kaitiakitanga",
            "manaakitanga": "manaakitanga",
            "taonga": "taonga",
            "rangatiratanga": "rangatiratanga",
            "mana": "mana",
            "tapu": "tapu",
            "kāwanatanga": "kawanatanga",
            "ture": "ture",
            "whānau": "whanau",
            "hapū": "hapu",
            "iwi": "iwi",
            "tikanga": "tikanga",
        }
        for token in doc:
            word = token.text
            # Clean punctuation to match dictionary
            clean_word = re.sub(r"[^\w\u0100-\u017F]", "", word)
            clean_word_lower = clean_word.lower()
            is_maori = clean_word in TE_REO_LEXICAL_ATOM_SET or is_macronized(clean_word)

            if is_maori:
                if clean_word_lower in tikanga_ontology:
                    ref = tikanga_ontology[clean_word_lower]
                    processed_tokens.append(f'<phrase xml:lang="mi" refersTo="#tikanga_{ref}">{word}</phrase>')
                else:
                    processed_tokens.append(f'<phrase xml:lang="mi">{word}</phrase>')
            else:
                processed_tokens.append(word)

            if token.whitespace_:
                processed_tokens.append(token.whitespace_)
        processed_text = "".join(processed_tokens)

        # Parse definitions (isomorphic isolation)
        definition_match = re.search(r'(“[^”]+”|"[^"]+"|\b[A-Za-z\s]+\b)\s+(means|includes)', processed_text, re.IGNORECASE)
        if definition_match:
            term = definition_match.group(1)
            processed_text = processed_text.replace(term, f"<definition>{term}</definition>", 1)

        import subprocess
        try:
            git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            git_commit = "unknown"
        from nlp_policy_nz import __version__

        lines: list[str] = []
        lines.append('<akomaNtoso xmlns="http://oasis-open.org">')
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
        lines.append('      <references source="#nlp_policy_nz">')
        lines.append(f'        <TLCConcept id="prov_pipeline_version" href="/ontology/concept/prov/pipeline_version" showAs="nlp-policy-nz-v{__version__}"/>')
        lines.append(f'        <TLCConcept id="prov_git_commit" href="/ontology/concept/prov/git_commit" showAs="{git_commit}"/>')
        lines.append("      </references>")
        lines.append("    </meta>")
        lines.append("    <body>")
        lines.append("      <mainBody>")
        lines.append("        <content>")
        lines.append(f"          <p>{processed_text}</p>")
        lines.append("        </content>")
        lines.append("      </mainBody>")
        lines.append("    </body>")
        lines.append(f"  </{struct_type}>")
        lines.append("</akomaNtoso>")

        # LegalRuleML Injection (Deontic Mapping)
        annotations = _modality_annotations(doc)
        if not annotations:
            try:
                annotations = _detect_modality_annotations(doc)
            except Exception:
                annotations = []

        if annotations:
            lines.append('<legalRuleML xmlns="http://oasis-open.org">')
            for idx, ann in enumerate(annotations):
                rule_id = f"rule_{chunk_id}_sub_{idx+1}"
                strength = ann.modality.value.capitalize()

                # Check for Exception patterns (Catala DSL isolation)
                is_exception = False
                if ann.scope and any(kw in ann.scope.lower() for kw in ["does not apply", "except", "unless", "provided that"]):
                    is_exception = True

                if is_exception:
                    lines.append(f'  <Rule id="{rule_id}_exception">')
                    lines.append("    <Strength>Exception</Strength>")
                    if idx > 0:
                        lines.append(f"    <AppliesTo>rule_{chunk_id}_sub_{idx}</AppliesTo>")
                    else:
                        lines.append(f"    <AppliesTo>rule_{chunk_id}_sub_1</AppliesTo>")
                    lines.append(f"    <Condition>{ann.scope}</Condition>")
                    lines.append("  </Rule>")
                else:
                    lines.append(f'  <Rule id="{rule_id}">')
                    lines.append(f"    <Strength>{strength}</Strength>")
                    lines.append("    <Actor>Subject</Actor>")
                    lines.append(f"    <Action>{ann.scope or ann.trigger}</Action>")
                    lines.append("  </Rule>")
            lines.append("</legalRuleML>")

        return "\n".join(lines)

    def _emit_parlacap_jsonl(self, doc: Doc, chunk_id: str, struct_type: str) -> str:
        """Serialize to ParlaCAP-JSONL containing joint syntax-aware token mappings."""
        tokens: list[dict[str, str | int]] = []
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
        data: dict[str, str | list[dict[str, str | int]]] = {
            "id": chunk_id,
            "country": self.config.country,
            "structural_type": struct_type,
            "tokens": tokens,
        }
        return json.dumps(data)

    def _emit_catala_dsl(self, doc: Doc, chunk_id: str, struct_type: str) -> str:
        """Serialize into an executable Catala DSL module template."""
        annotations = _modality_annotations(doc)
        if not annotations:
            try:
                annotations = _detect_modality_annotations(doc)
            except Exception:
                annotations = []

        lines: list[str] = []
        struct_name = "".join(x.title() for x in chunk_id.replace("-", "_").split("_"))
        lines.append(f"# {struct_type.capitalize()} {chunk_id}")
        lines.append(f"declaration structure {struct_name}:")

        conditions: list[str] = []
        actions: list[tuple[str, str]] = []

        for ann in annotations:
            strength = ann.modality.value
            action = ann.scope or ann.trigger

            # Simple sanitization for variable names
            var_action = re.sub(r"[^a-zA-Z0-9_]", "_", action.lower()).strip("_")
            var_action = re.sub(r"_+", "_", var_action)[:40]

            is_exception = False
            if ann.scope and any(kw in ann.scope.lower() for kw in ["does not apply", "except", "unless", "provided that"]):
                is_exception = True

            if is_exception:
                conditions.append(var_action)
            else:
                actions.append((var_action, strength))

        lines.append("  input applicant: boolean")
        for cond in conditions:
            lines.append(f"  input {cond}: boolean")
        for act, _strength in actions:
            lines.append(f"  output {act}: boolean")

        lines.append("")

        for act, strength in actions:
            lines.append(f"rule {struct_name}.{act} equals")
            val = "true" if strength in ("obligation", "permission") else "false"

            if conditions:
                condition_terms: list[str] = [f"not {condition}" for condition in conditions]
                cond_str = " and ".join(condition_terms)
                lines.append(f"  {val} under condition")
                lines.append(f"    {cond_str}")
                lines.append("  otherwise false")
            else:
                lines.append(f"  {val}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 6. SOTA Annotation Visualizer (displaCy Bridge)
# ---------------------------------------------------------------------------


class SOTAPipelineVisualizer:
    """Exports clean, styled HTML markup of document annotations via displaCy."""

    @staticmethod
    def generate_html_report(doc: Doc, output_path: str | None = None) -> str:
        """Generate static HTML rendering sentence boundaries and entity tags."""
        colors = {
            "LAW": "linear-gradient(90deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%)",
            "SECTION": "linear-gradient(90deg, #a1c4fd 0%, #c2e9fb 100%)",
            "PRELIM": "linear-gradient(90deg, #fdfcfb 0%, #e2d1c3 100%)",
        }
        options = {"colors": colors}

        # We temporarily copy SpanGroups into doc.ents to display them inside displaCy
        # as displaCy focuses on doc.ents for rendering structural highlighting.
        spans = _span_group(doc, "nz_nested_entities")
        original_ents = doc.ents

        ents_to_set: list[Span] = []
        for span in spans:
            struct_type = _span_extension_text(span, "nz_legislation_parlamint_tei_ana_structural_type", "PRELIM")
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
    """Run the configured framework over raw data."""
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
    """Run the demonstration pipeline."""
    config_nz = FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="XML",
        target_schema_standard="ParlaMint-TEI-Ana",
    )
    doc = run_framework(config_nz, SAMPLE_XML)

    nested_spans = _span_group(doc, "nz_nested_entities")
    for _span in nested_spans:
        pass

    # Generates static HTML displaying our highlighted entities
    SOTAPipelineVisualizer.generate_html_report(doc, "conductor/annotation_report.html")


if __name__ == "__main__":
    run_demo()
