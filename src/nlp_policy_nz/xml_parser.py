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
New Zealand Legislative XML Parser and spaCy v3 Structure Ingestion Pipeline.
Consumes structured PCO XML, extracts clean text, maps character boundaries,
and registers custom spaCy metadata extensions.
"""

import re
import typing as ty
from bs4 import BeautifulSoup, Tag
import msgspec
import spacy
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span


# ---------------------------------------------------------------------------
# 1. Structured Data Types via msgspec
# ---------------------------------------------------------------------------

class XMLElementMetadata(msgspec.Struct):
    """Holds character offsets and attributes of parsed XML legislative blocks."""
    element_type: str        # e.g., 'act', 'part', 'section', 'heading'
    start_char: int
    end_char: int
    element_id: ty.Optional[str] = None
    element_title: ty.Optional[str] = None


# Register custom spaCy extensions
if not Doc.has_extension("nz_xml_metadata"):
    Doc.set_extension("nz_xml_metadata", default=[])

if not Span.has_extension("nz_element_type"):
    Span.set_extension("nz_element_type", default=None)

if not Span.has_extension("nz_element_id"):
    Span.set_extension("nz_element_id", default=None)

if not Span.has_extension("nz_element_title"):
    Span.set_extension("nz_element_title", default=None)


# ---------------------------------------------------------------------------
# 2. XML Parser and Character Offset Mapper
# ---------------------------------------------------------------------------

class LegislativeXMLParser:
    """Parses NZ legislation XML, extracting clean text and mapping elements to offsets."""

    def __init__(self, xml_text: str):
        self.soup = BeautifulSoup(xml_text, "xml")
        self.clean_text_buffer: ty.List[str] = []
        self.current_offset = 0
        self.metadata: ty.List[XMLElementMetadata] = []

    def _append_text(self, text: str) -> None:
        """Appends text to the buffer and updates character offsets."""
        self.clean_text_buffer.append(text)
        self.current_offset += len(text)

    def _traverse(self, element: ty.Union[Tag, str]) -> None:
        """Recursively parses XML tags while tracking plain text character boundaries."""
        if isinstance(element, str):
            self._append_text(element)
            return

        tag_name = element.name
        start = self.current_offset
        
        # Capture element specific metadata
        element_id = element.get("id")
        element_title = element.get("title")

        # Recurse children
        for child in element.children:
            self._traverse(child)

        end = self.current_offset

        # Save metadata for targeted structural tags
        if tag_name in ("act", "part", "section", "heading", "para"):
            self.metadata.append(
                XMLElementMetadata(
                    element_type=tag_name,
                    start_char=start,
                    end_char=end,
                    element_id=element_id,
                    element_title=element_title,
                )
            )

    def parse(self) -> ty.Tuple[str, ty.List[XMLElementMetadata]]:
        """Executes the parsing and returns clean text alongside metadata array."""
        root = self.soup.find()
        if root is not None:
            self._traverse(root)
        clean_text = "".join(self.clean_text_buffer)
        return clean_text, self.metadata


# ---------------------------------------------------------------------------
# 3. Custom spaCy v3 Components
# ---------------------------------------------------------------------------

@Language.component("nz_xml_structure_injector")
def nz_xml_structure_injector(doc: Doc) -> Doc:
    """
    Custom spaCy component mapping pre-calculated XML character bounds to Doc Spans.
    Injects element attributes into custom metadata properties.
    """
    metadata_list: ty.List[XMLElementMetadata] = doc._.nz_xml_metadata
    spans: ty.List[Span] = []

    for meta in metadata_list:
        # Resolve character offsets to token indexes
        span = doc.char_span(meta.start_char, meta.end_char, alignment_mode="expand")
        if span is not None:
            # Set the custom structural extensions
            span._.nz_element_type = meta.element_type
            span._.nz_element_id = meta.element_id
            span._.nz_element_title = meta.element_title
            spans.append(span)

    # Filter overlaps (preferring longer/outer spans in the hierarchy)
    filtered_spans = spacy.util.filter_spans(spans)
    
    # Store in standard doc.spans dictionary under a custom group name
    doc.spans["nz_xml_structure"] = filtered_spans
    return doc


@Language.component("nz_cross_reference_matcher")
def nz_cross_reference_matcher(doc: Doc) -> Doc:
    """
    Custom spaCy component utilizing rule-based Matcher to identify internal 
    legislative cross-references (e.g. section 5(2)(b) or Part 3).
    """
    matcher = Matcher(doc.vocab)

    # Patterns for: section 5, section 5(2), section 5(2)(b)
    section_pattern = [
        {"LOWER": "section"},
        {"IS_DIGIT": True},
        {"TEXT": {"REGEX": r"^\(\d+\)(?:\([a-z]\))?$"}, "OP": "?"},
    ]

    # Patterns for: Part 3, Part II
    part_pattern = [
        {"LOWER": "part"},
        {"TEXT": {"REGEX": r"^(?:\d+|[IVXLCDM]+)$"}},
    ]

    matcher.add("LEGISLATION_SECTION", [section_pattern])
    matcher.add("LEGISLATION_PART", [part_pattern])

    matches = matcher(doc)
    spans: ty.List[Span] = []

    for match_id, start, end in matches:
        label = doc.vocab.strings[match_id]
        span = Span(doc, start, end, label=label)
        spans.append(span)

    doc.spans["nz_cross_references"] = spacy.util.filter_spans(spans)
    return doc


# ---------------------------------------------------------------------------
# 4. Pipeline Assembly and Execution Demo
# ---------------------------------------------------------------------------

SAMPLE_NZ_XML = """
<act id="2026-001" title="Legislative Test Act 2026">
    <part id="P1" title="Preliminary Provisions">
        <heading>Part 1: Introductory Clauses</heading>
        <section id="S1">
            <heading>1 Purpose</heading>
            <para>The purpose of this Act is to check custom tokenizers.</para>
        </section>
        <section id="S2">
            <heading>2 Interpretation</heading>
            <para>Under section 1 of this Act, definitions apply. See also Part 1 for details.</para>
        </section>
    </part>
</act>
"""

def run_demo() -> None:
    """Runs the legislative parser demo, printing structure and cross-references."""
    print("[Pipeline] Parsing XML structure...")
    parser = LegislativeXMLParser(SAMPLE_NZ_XML)
    clean_text, metadata = parser.parse()

    print("\n--- Clean Text Extracted ---")
    print(clean_text)

    # Load base pipeline
    print("\n[Pipeline] Initializing spaCy model...")
    nlp = spacy.blank("en")

    # Add custom components to the pipeline
    nlp.add_pipe("nz_xml_structure_injector", first=True)
    nlp.add_pipe("nz_cross_reference_matcher", after="nz_xml_structure_injector")

    # Parse document and inject XML metadata beforehand
    doc = nlp.make_doc(clean_text)
    doc._.nz_xml_metadata = metadata

    # Process doc through pipeline
    doc = nlp(doc)

    print("\n--- Injected Legislative Structural Metadata Spans ---")
    for span in doc.spans.get("nz_xml_structure", []):
        print(
            f"Type: {span._.nz_element_type:<8} | "
            f"ID: {str(span._.nz_element_id):<6} | "
            f"Title: {str(span._.nz_element_title):<24} | "
            f"Text: '{span.text.strip()}'"
        )

    print("\n--- Extracted Internal Cross-References ---")
    for span in doc.spans.get("nz_cross_references", []):
        print(f"Reference Type: {span.label_:<18} | Text: '{span.text}'")


if __name__ == "__main__":
    run_demo()
