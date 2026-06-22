"""Tests for Track 10 deontic modality detection.

Test classes mirror the structure of :mod:`test_feature_extraction` and cover
pattern matching, scope resolution, convenience API, and annotation data.
"""

from __future__ import annotations

import pytest
import spacy

from nlp_policy_nz.legal.modality import (
    DeonticModality,
    DeonticModalityDetector,
    ModalityAnnotation,
    detect_modality,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def nlp() -> spacy.Language:
    """Build an ``en_core_web_sm`` pipeline with the deontic modality component."""
    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        _nlp = spacy.blank("en")
        _nlp.add_pipe("sentencizer")
    after = "parser" if "parser" in _nlp.pipe_names else None
    _nlp.add_pipe("deontic_modality", after=after)
    return _nlp


# ---------------------------------------------------------------------------
# Deontic Pattern Tests
# ---------------------------------------------------------------------------


class TestDeonticPatterns:
    """Tests for deontic modality pattern matching."""

    def test_must_detected(self, nlp: spacy.Language) -> None:
        """``must`` is detected as OBLIGATION."""
        annotations = detect_modality("The chief executive must keep a register.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.OBLIGATION
        assert annotations[0].trigger == "must"

    def test_shall_detected(self, nlp: spacy.Language) -> None:
        """``shall`` is detected as OBLIGATION."""
        annotations = detect_modality("The agency shall publish the notice.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.OBLIGATION
        assert annotations[0].trigger == "shall"

    def test_must_not_detected(self, nlp: spacy.Language) -> None:
        """``must not`` is detected as PROHIBITION (multi-token before single)."""
        annotations = detect_modality("A person must not disclose protected information.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.PROHIBITION
        assert annotations[0].trigger == "must not"

    def test_shall_not_detected(self, nlp: spacy.Language) -> None:
        """``shall not`` is detected as PROHIBITION."""
        annotations = detect_modality("The defendant shall not remove evidence.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.PROHIBITION
        assert annotations[0].trigger == "shall not"

    def test_may_detected(self, nlp: spacy.Language) -> None:
        """``may`` is detected as PERMISSION."""
        annotations = detect_modality("The Minister may approve the amendment.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.PERMISSION
        assert annotations[0].trigger == "may"

    def test_need_not_detected(self, nlp: spacy.Language) -> None:
        """``need not`` is detected as DISPENSATION."""
        annotations = detect_modality("The applicant need not attend the hearing.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.DISPENSATION
        assert annotations[0].trigger == "need not"

    def test_no_modality(self, nlp: spacy.Language) -> None:
        """Text without deontic modals produces an empty annotation list."""
        annotations = detect_modality("The committee met on Monday.", nlp)
        assert annotations == []

    def test_empty_text(self, nlp: spacy.Language) -> None:
        """Empty string produces an empty annotation list."""
        annotations = detect_modality("", nlp)
        assert annotations == []

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_capitalised_must(self, nlp: spacy.Language) -> None:
        """Capitalised ``Must`` is detected identically to lower-case ``must``."""
        annotations = detect_modality("Must the agency comply?", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.OBLIGATION
        assert annotations[0].trigger == "Must"

    def test_capitalised_shall_not(self, nlp: spacy.Language) -> None:
        """Capitalised ``Shall Not`` is still matched as a multi-token pattern."""
        annotations = detect_modality("Shall Not the board act?", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.PROHIBITION
        assert annotations[0].trigger == "Shall Not"

    def test_modal_at_sentence_start(self, nlp: spacy.Language) -> None:
        """Modals are detected when the deontic trigger begins the sentence."""
        annotations = detect_modality("May the applicant submit new evidence.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.PERMISSION

    def test_modal_at_sentence_middle(self, nlp: spacy.Language) -> None:
        """Modals are detected mid-sentence."""
        annotations = detect_modality("The board shall approve the budget.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.OBLIGATION
        assert annotations[0].trigger == "shall"

    def test_multiple_modals_one_sentence(self, nlp: spacy.Language) -> None:
        """Multiple deontic triggers in a single sentence annotated separately."""
        annotations = detect_modality(
            "The Minister must approve and may amend the regulation.", nlp
        )
        assert len(annotations) == 2
        assert annotations[0].modality == DeonticModality.OBLIGATION
        assert annotations[0].trigger == "must"
        assert annotations[1].modality == DeonticModality.PERMISSION
        assert annotations[1].trigger == "may"

    def test_modal_after_comma(self, nlp: spacy.Language) -> None:
        """Modals following a comma are still matched correctly."""
        annotations = detect_modality("If the Minister agrees, the department may proceed.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.PERMISSION
        assert annotations[0].trigger == "may"


# ---------------------------------------------------------------------------
# Scope Resolution Tests
# ---------------------------------------------------------------------------


class TestScopeResolution:
    """Tests for dependency-based deontic scope resolution."""

    def test_simple_scope(self, nlp: spacy.Language) -> None:
        """Scope captures the verb phrase governed by the deontic trigger."""
        annotations = detect_modality("The Minister must appoint a committee.", nlp)
        assert len(annotations) == 1
        assert annotations[0].scope == "appoint a committee"

    def test_scope_with_object(self, nlp: spacy.Language) -> None:
        """Scope includes direct object of the governed verb."""
        annotations = detect_modality("The applicant shall provide evidence.", nlp)
        assert len(annotations) == 1
        assert annotations[0].scope == "provide evidence"

    def test_scope_with_negation(self, nlp: spacy.Language) -> None:
        """Scope captures the verb phrase following a prohibition trigger."""
        annotations = detect_modality("A person must not remove evidence.", nlp)
        assert len(annotations) == 1
        assert annotations[0].scope == "remove evidence"

    def test_scope_with_adverbial_modifier(self, nlp: spacy.Language) -> None:
        """Scope includes adverbial modifiers attached to the governed verb."""
        annotations = detect_modality("The authority shall promptly notify the public.", nlp)
        assert len(annotations) == 1
        assert annotations[0].scope is not None
        assert "notify" in annotations[0].scope
        assert "promptly" in annotations[0].scope or "public" in annotations[0].scope

    def test_scope_with_prepositional_phrase(self, nlp: spacy.Language) -> None:
        """Scope includes prepositional phrases modifying the governed verb."""
        annotations = detect_modality("The board must report to the Minister.", nlp)
        assert len(annotations) == 1
        assert annotations[0].scope is not None
        assert "report" in annotations[0].scope
        assert "to" in annotations[0].scope

    def test_scope_no_verb_fallback(self, nlp: spacy.Language) -> None:
        """When the trigger head is not a verb, the fallback captures text
        after the trigger until punctuation.
        """
        annotations = detect_modality("The applicant must the form.", nlp)
        assert len(annotations) == 1
        if annotations[0].scope is not None:
            assert "the form" in annotations[0].scope

    def test_scope_multiple_sentences(self, nlp: spacy.Language) -> None:
        """Scope does not cross sentence boundaries."""
        annotations = detect_modality(
            "The Minister must decide. The committee may review later.", nlp
        )
        assert len(annotations) == 2
        assert annotations[0].scope is not None
        assert "decide" in annotations[0].scope


# ---------------------------------------------------------------------------
# Convenience Function Tests
# ---------------------------------------------------------------------------


class TestDetectModality:
    """Tests for the :func:`detect_modality` convenience function."""

    def test_detect_modality_convenience(self, nlp: spacy.Language) -> None:
        """``detect_modality`` returns annotations for a single-modal sentence."""
        annotations = detect_modality("The agency must comply.", nlp)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.OBLIGATION

    def test_multiple_modalities(self, nlp: spacy.Language) -> None:
        """A section containing multiple modals returns all annotations."""
        annotations = detect_modality(
            "The Minister must appoint a committee. "
            "The committee may establish subcommittees. "
            "A member shall not vote on their own interest.",
            nlp,
        )
        assert len(annotations) == 3
        expected = [
            DeonticModality.OBLIGATION,
            DeonticModality.PERMISSION,
            DeonticModality.PROHIBITION,
        ]
        assert [a.modality for a in annotations] == expected

    def test_auto_adds_pipe(self) -> None:
        """``detect_modality`` adds the component automatically when missing."""
        nlp_auto = spacy.blank("en")
        nlp_auto.add_pipe("sentencizer")
        annotations = detect_modality("The applicant must respond.", nlp_auto)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.OBLIGATION
        assert "deontic_modality" in nlp_auto.pipe_names
        annotations2 = detect_modality("The board shall approve.", nlp_auto)
        assert len(annotations2) == 1

    def test_detect_modality_empty_text(self, nlp: spacy.Language) -> None:
        """Empty text returns an empty list."""
        assert detect_modality("", nlp) == []

    def test_detect_modality_no_modals(self, nlp: spacy.Language) -> None:
        """Text without modals returns an empty list."""
        assert detect_modality("Regular text without any modal verbs.", nlp) == []


# ---------------------------------------------------------------------------
# Annotation Data Class Tests
# ---------------------------------------------------------------------------


class TestModalityAnnotation:
    """Tests for the :class:`ModalityAnnotation` dataclass."""

    def test_annotation_repr(self) -> None:
        """``__repr__`` includes key fields."""
        annotation = ModalityAnnotation(
            modality=DeonticModality.OBLIGATION,
            trigger="must",
            scope="comply",
            start=10,
            end=14,
        )
        representation = repr(annotation)
        assert "OBLIGATION" in representation
        assert "must" in representation
        assert "comply" in representation

    def test_annotation_default_scope(self) -> None:
        """``scope`` can be ``None``."""
        annotation = ModalityAnnotation(
            modality=DeonticModality.PERMISSION,
            trigger="may",
            scope=None,
            start=0,
            end=3,
        )
        assert annotation.scope is None

    def test_annotation_to_dict(self) -> None:
        """``to_dict`` returns a dictionary with string modality value."""
        annotation = ModalityAnnotation(
            modality=DeonticModality.PROHIBITION,
            trigger="must not",
            scope="disclose",
            start=15,
            end=23,
        )
        data = annotation.to_dict()
        assert data["modality"] == "prohibition"
        assert data["trigger"] == "must not"
        assert data["scope"] == "disclose"
        assert data["start"] == 15
        assert data["end"] == 23

    def test_annotation_frozen(self) -> None:
        """ModalityAnnotation instances are frozen (immutable)."""
        annotation = ModalityAnnotation(
            modality=DeonticModality.OBLIGATION,
            trigger="shall",
            scope="comply",
            start=5,
            end=10,
        )
        with pytest.raises(AttributeError):
            annotation.trigger = "may"  # type: ignore[misc]

    def test_annotation_equality(self) -> None:
        """Two annotations with identical fields are equal."""
        a1 = ModalityAnnotation(
            modality=DeonticModality.OBLIGATION,
            trigger="must",
            scope="comply",
            start=0,
            end=4,
        )
        a2 = ModalityAnnotation(
            modality=DeonticModality.OBLIGATION,
            trigger="must",
            scope="comply",
            start=0,
            end=4,
        )
        assert a1 == a2
        assert hash(a1) == hash(a2)


# ---------------------------------------------------------------------------
# Token / Doc Extension Tests
# ---------------------------------------------------------------------------


class TestDocTokenExtensions:
    """Tests for spaCy token and doc extensions populated by the detector."""

    def test_token_modality_extension(self, nlp: spacy.Language) -> None:
        """``token._.modality`` holds the modality value string."""
        doc = nlp("The agency shall publish the notice.")
        modal = next(token for token in doc if token.text == "shall")
        assert modal._.modality == "obligation"

    def test_modality_scope_extension(self, nlp: spacy.Language) -> None:
        """``token._.modality_scope`` holds the resolved scope text."""
        doc = nlp("The agency shall publish the notice.")
        modal = next(token for token in doc if token.text == "shall")
        assert modal._.modality_scope == "publish the notice"

    def test_modality_annotation_extension(self, nlp: spacy.Language) -> None:
        """``token._.modality_annotation`` references the full annotation."""
        doc = nlp("The agency shall publish the notice.")
        modal = next(token for token in doc if token.text == "shall")
        assert modal._.modality_annotation is doc._.modality_annotations[0]

    def test_doc_modality_annotations(self, nlp: spacy.Language) -> None:
        """``doc._.modality_annotations`` lists all annotations for the doc."""
        doc = nlp("The Minister must approve. The board may review.")
        annotations = doc._.modality_annotations
        assert len(annotations) == 2
        assert annotations[0].modality == DeonticModality.OBLIGATION
        assert annotations[1].modality == DeonticModality.PERMISSION

    def test_non_modal_token_has_none(self, nlp: spacy.Language) -> None:
        """Non-modal tokens have ``None`` extensions."""
        doc = nlp("The committee met on Monday.")
        for token in doc:
            assert token._.modality is None
            assert token._.modality_scope is None
            assert token._.modality_annotation is None


# ---------------------------------------------------------------------------
# Component Factory Tests
# ---------------------------------------------------------------------------


class TestDeonticModalityDetector:
    """Tests for the ``DeonticModalityDetector`` component class."""

    def test_factory_returns_detector(self, nlp: spacy.Language) -> None:
        """The ``deontic_modality`` factory creates a ``DeonticModalityDetector``."""
        detector = nlp.get_pipe("deontic_modality")
        assert isinstance(detector, DeonticModalityDetector)

    def test_custom_patterns(self) -> None:
        """Custom patterns override the defaults."""
        custom_patterns = {
            "must": {
                "modality": DeonticModality.OBLIGATION.value,
                "tokens": ("must",),
            },
        }
        nlp_custom = spacy.blank("en")
        nlp_custom.add_pipe("sentencizer")
        nlp_custom.add_pipe(
            "deontic_modality",
            config={"patterns": custom_patterns},
        )
        annotations = detect_modality("The CEO must report.", nlp_custom)
        assert len(annotations) == 1
        assert annotations[0].modality == DeonticModality.OBLIGATION
        annotations2 = detect_modality("The CEO may approve.", nlp_custom)
        assert annotations2 == []

    def test_from_disk_returns_self(self, nlp: spacy.Language) -> None:
        """``from_disk`` returns ``self`` (no-op serialization)."""
        detector = nlp.get_pipe("deontic_modality")
        result = detector.from_disk("/nonexistent/path")
        assert result is detector

    def test_to_disk_no_error(self, nlp: spacy.Language) -> None:
        """``to_disk`` does not raise (no-op serialization)."""
        detector = nlp.get_pipe("deontic_modality")
        detector.to_disk("/nonexistent/path")
