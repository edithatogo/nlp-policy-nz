"""Akoma Ntoso v3 document emitters and local validation helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace
from html import escape
from typing import TYPE_CHECKING, Final, Protocol
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

AKN_NS: Final[str] = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
OASIS_AKN_V3_XSD_URL: Final[str] = (
    "https://docs.oasis-open.org/legaldocml/akn-core/v1.0/os/part2-specs/"
    "schemas/akomantoso30.xsd"
)
SUPPORTED_DOCUMENT_TYPES: Final[set[str]] = {"amendment", "bill", "debate", "judgment"}


@dataclass(frozen=True)
class FRBRMetadata:
    """Metadata required to construct the AKN FRBR hierarchy."""

    country: str
    document_type: str
    identifier: str
    date: str = "1970-01-01"
    author: str = "nlp-policy-nz"
    language: str = "eng"
    version: str = "1"

    def with_type(self, document_type: str) -> FRBRMetadata:
        """Return a copy of this metadata with another document type."""
        return replace(self, document_type=document_type)

    @property
    def work_uri(self) -> str:
        """Return the FRBR Work URI."""
        return f"/{self.country}/{self.document_type}/{self.identifier}"

    @property
    def expression_uri(self) -> str:
        """Return the FRBR Expression URI."""
        return f"{self.work_uri}/{self.language}@{self.date}"

    @property
    def manifestation_uri(self) -> str:
        """Return the FRBR Manifestation URI."""
        return f"{self.expression_uri}/main.xml"

    @property
    def item_uri(self) -> str:
        """Return the FRBR Item URI."""
        return f"{self.manifestation_uri}#v{self.version}"


@dataclass(frozen=True)
class AKNDocument:
    """Generated AKN XML plus document metadata."""

    xml: str
    document_type: str
    metadata: FRBRMetadata


@dataclass(frozen=True)
class AKNValidationResult:
    """Result of XSD-backed AKN validation."""

    valid: bool
    errors: list[str]
    schema_source: str = OASIS_AKN_V3_XSD_URL


class AKNValidationError(ValueError):
    """Raised when AKN validation cannot run or the document is invalid."""


class _SchemaValidationError(Protocol):
    """Protocol for xmlschema validation error objects."""

    reason: str


class _XMLSchemaValidator(Protocol):
    """Protocol for compiled XML Schema validators."""

    def iter_errors(self, source: str) -> Iterable[_SchemaValidationError]:
        """Yield validation errors for an XML source string."""


def _q(tag: str) -> str:
    """Return a namespaced AKN tag."""
    return f"{{{AKN_NS}}}{tag}"


def _load_xml_schema(schema_source: str | Path) -> _XMLSchemaValidator:
    """Load a compiled XML Schema validator from a URL or local path."""
    try:
        import xmlschema
    except ImportError as exc:
        msg = "AKN XSD validation requires the xmlschema package."
        raise AKNValidationError(msg) from exc

    try:
        return xmlschema.XMLSchema(str(schema_source))
    except Exception as exc:
        msg = f"Unable to load AKN XML Schema from {schema_source}: {exc}"
        raise AKNValidationError(msg) from exc


def _frbr_block(metadata: FRBRMetadata) -> str:
    """Emit the full AKN FRBR hierarchy."""
    return "\n".join(
        [
            '<identification source="#nlp_policy_nz">',
            "  <FRBRWork>",
            f'    <FRBRthis value="{metadata.work_uri}/main"/>',
            f'    <FRBRuri value="{metadata.work_uri}"/>',
            f'    <FRBRdate date="{metadata.date}" name="generation"/>',
            f'    <FRBRauthor href="#{metadata.author}" as="#author"/>',
            f'    <FRBRcountry value="{metadata.country}"/>',
            "  </FRBRWork>",
            "  <FRBRExpression>",
            f'    <FRBRthis value="{metadata.expression_uri}/main"/>',
            f'    <FRBRuri value="{metadata.expression_uri}"/>',
            f'    <FRBRdate date="{metadata.date}" name="generation"/>',
            f'    <FRBRauthor href="#{metadata.author}" as="#author"/>',
            f'    <FRBRlanguage language="{metadata.language}"/>',
            "  </FRBRExpression>",
            "  <FRBRManifestation>",
            f'    <FRBRthis value="{metadata.manifestation_uri}"/>',
            f'    <FRBRuri value="{metadata.manifestation_uri}"/>',
            f'    <FRBRdate date="{metadata.date}" name="generation"/>',
            f'    <FRBRauthor href="#{metadata.author}" as="#author"/>',
            "  </FRBRManifestation>",
            "  <FRBRItem>",
            f'    <FRBRthis value="{metadata.item_uri}"/>',
            f'    <FRBRuri value="{metadata.item_uri}"/>',
            f'    <FRBRdate date="{metadata.date}" name="generation"/>',
            f'    <FRBRauthor href="#{metadata.author}" as="#author"/>',
            "  </FRBRItem>",
            "</identification>",
        ]
    )


def _references_block(references: list[tuple[str, str]]) -> str:
    """Emit AKN references metadata."""
    rows = ['<references source="#nlp_policy_nz">']
    for ref_id, href in references:
        rows.append(
            f'  <TLCReference name="{escape(ref_id, quote=True)}" '
            f'href="{escape(href, quote=True)}" showAs="{escape(ref_id)}"/>'
        )
    rows.append('  <TLCEvent href="#generation" showAs="generation"/>')
    rows.append("</references>")
    return "\n".join(rows)


def _events_block(events: list[tuple[str, str]]) -> str:
    """Emit AKN lifecycle event references."""
    rows = ['<lifecycle source="#nlp_policy_nz">']
    for event_id, date in events:
        rows.append(
            f'  <eventRef date="{escape(date, quote=True)}" '
            f'source="#nlp_policy_nz" type="{escape(event_id, quote=True)}" '
            f'href="#{escape(event_id, quote=True)}"/>'
        )
    rows.append("</lifecycle>")
    return "\n".join(rows)


def _analysis_block(analysis: list[tuple[str, str]]) -> str:
    """Emit analysis metadata."""
    rows = ['<analysis source="#nlp_policy_nz">']
    for key, _value in analysis:
        rows.append(f'  <otherAnalysis source="#{escape(key, quote=True)}"/>')
    rows.append("</analysis>")
    return "\n".join(rows)


def _body_block(tag: str, body: list[str]) -> str:
    """Serialize body text into the official container for a document type."""
    if tag == "bill":
        return _bill_body(body)
    if tag == "amendment":
        return _amendment_body(body)
    if tag == "debate":
        return _debate_body(body)
    if tag == "judgment":
        return _judgment_body(body)
    msg = f"Unsupported AKN document type: {tag}"
    raise ValueError(msg)


def _bill_body(body: list[str]) -> str:
    """Serialize bill text as AKN sections."""
    rows = ["    <body>"]
    for index, text in enumerate(body, start=1):
        rows.extend(
            [
                f'      <section eId="sec_{index}">',
                f"        <num>{index}</num>",
                f"        <content><p>{escape(text)}</p></content>",
                "      </section>",
            ]
        )
    rows.append("    </body>")
    return "\n".join(rows)


def _amendment_body(body: list[str]) -> str:
    """Serialize amendment text as AKN amendment content."""
    rows = ["    <amendmentBody>"]
    for text in body:
        rows.append(f"      <amendmentContent><p>{escape(text)}</p></amendmentContent>")
    rows.append("    </amendmentBody>")
    return "\n".join(rows)


def _debate_body(body: list[str]) -> str:
    """Serialize debate text as an AKN debate section."""
    rows = ["    <debateBody>", '      <debateSection name="general">']
    for text in body:
        rows.append(f"        <p>{escape(text)}</p>")
    rows.extend(["      </debateSection>", "    </debateBody>"])
    return "\n".join(rows)


def _judgment_body(body: list[str]) -> str:
    """Serialize judgment text as an AKN decision block."""
    rows = ["    <header></header>", "    <judgmentBody>", "      <decision>"]
    for text in body:
        rows.append(f"        <p>{escape(text)}</p>")
    rows.extend(["      </decision>", "    </judgmentBody>"])
    return "\n".join(rows)


def _emit_document(
    metadata: FRBRMetadata,
    title: str,
    body: list[str],
    *,
    tag: str,
    references: list[tuple[str, str]] | None = None,
    events: list[tuple[str, str]] | None = None,
    analysis: list[tuple[str, str]] | None = None,
) -> str:
    """Emit an AKN document for a supported document type."""
    if tag not in SUPPORTED_DOCUMENT_TYPES:
        msg = f"Unsupported AKN document type: {tag}"
        raise ValueError(msg)
    metadata = metadata.with_type(tag)
    refs = references or [("nlp_policy_nz", "/ontology/source/nlp_policy_nz")]
    evts = events or [("generation", metadata.date)]
    analyses = analysis or [("pipeline", "nlp-policy-nz")]
    escaped_title = escape(title)

    return "\n".join(
        [
            f'<akomaNtoso xmlns="{AKN_NS}">',
            f'  <{tag} name="{escaped_title}">',
            "    <meta>",
            _indent(_frbr_block(metadata), 6),
            _indent(_events_block(evts), 6),
            _indent(_analysis_block(analyses), 6),
            _indent(_references_block(refs), 6),
            "    </meta>",
            _body_block(tag, body),
            f"  </{tag}>",
            "</akomaNtoso>",
        ]
    )


def _indent(text: str, spaces: int) -> str:
    """Indent a multiline XML fragment."""
    prefix = " " * spaces
    return "\n".join(f"{prefix}{line}" for line in text.splitlines())


def emit_bill(
    metadata: FRBRMetadata,
    title: str,
    body: list[str],
    *,
    references: list[tuple[str, str]] | None = None,
    events: list[tuple[str, str]] | None = None,
    analysis: list[tuple[str, str]] | None = None,
) -> str:
    """Emit an AKN bill document."""
    return _emit_document(
        metadata,
        title,
        body,
        tag="bill",
        references=references,
        events=events,
        analysis=analysis,
    )


def emit_amendment(metadata: FRBRMetadata, title: str, body: list[str]) -> str:
    """Emit an AKN amendment document."""
    return _emit_document(metadata, title, body, tag="amendment")


def emit_judgment(metadata: FRBRMetadata, title: str, body: list[str]) -> str:
    """Emit an AKN judgment document."""
    return _emit_document(metadata, title, body, tag="judgment")


def emit_debate(metadata: FRBRMetadata, title: str, body: list[str]) -> str:
    """Emit an AKN debate document."""
    return _emit_document(metadata, title, body, tag="debate")


class AKNValidator:
    """XSD-backed validator for generated Akoma Ntoso v3 XML."""

    def __init__(self, schema_source: str | Path = OASIS_AKN_V3_XSD_URL) -> None:
        """Initialize the instance."""
        self.schema_source = str(schema_source)
        self._schema = _load_xml_schema(schema_source)

    def validate(self, xml: str) -> AKNValidationResult:
        """Validate an AKN XML document against the configured XSD."""
        try:
            root = ET.fromstring(xml)  # noqa: S314 - syntax check before XSD validation.
        except ET.ParseError as exc:
            return AKNValidationResult(False, [f"XML parse error: {exc}"], self.schema_source)

        if root.tag != _q("akomaNtoso"):
            return AKNValidationResult(
                False,
                ["Root element must be akomaNtoso in the AKN v3 namespace."],
                self.schema_source,
            )

        errors = [error.reason for error in self._schema.iter_errors(xml)]
        return AKNValidationResult(not errors, errors, self.schema_source)

    def validate_or_raise(self, xml: str) -> AKNValidationResult:
        """Validate XML and raise if it is not valid for the configured XSD."""
        result = self.validate(xml)
        if not result.valid:
            raise AKNValidationError("; ".join(result.errors))
        return result
