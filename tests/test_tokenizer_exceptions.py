"""Tests for tokenizer exceptions in the Māori Language Guard module."""

from __future__ import annotations

import spacy
from spacy import util as spacy_util

from nlp_policy_nz.guard.tokenizer_exceptions import (
    TE_REO_LEXICAL_ATOM_SET,
    TE_REO_PREFIXES,
    _maori_guard_component,
    build_tokenizer_exceptions,
    create_maori_guard_component,
)


class TestTeReoLexicalAtomSet:
    """Test suite for :data:`TE_REO_LEXICAL_ATOM_SET`."""

    _KEY_WORDS: tuple[str, ...] = (
        "tikanga",
        "taonga",
        "kāwanatanga",
        "Whakawā",
        "koutou",
        "Māori",
        "Pākehā",
        "Aotearoa",
        "whānau",
        "hapū",
        "iwi",
        "rohe",
        "kōrero",
        "whakapapa",
        "wānanga",
        "mana",
        "tapu",
        "noa",
        "utu",
        "koha",
        "aroha",
        "whakaminenga",
        "tiriti",
        "rangatiratanga",
        "motuhake",
        "whakahaere",
        "pūtea",
    )

    def test_te_reo_lexical_atom_set_contains_key_words(self) -> None:
        """Check that important Te Reo words are present in the atom set."""
        missing = [w for w in self._KEY_WORDS if w not in TE_REO_LEXICAL_ATOM_SET]
        assert not missing, f"Missing atoms: {missing}"

    def test_te_reo_lexical_atom_set_has_at_least_twenty_items(self) -> None:
        """The set should contain at least 20 entries."""
        assert len(TE_REO_LEXICAL_ATOM_SET) >= 20  # noqa: PLR2004

    def test_te_reo_lexical_atom_set_is_frozenset_of_strings(self) -> None:
        """Verify the type of the exported constant."""
        assert isinstance(TE_REO_LEXICAL_ATOM_SET, frozenset)
        assert all(isinstance(w, str) for w in TE_REO_LEXICAL_ATOM_SET)


class TestTeReoPrefixes:
    """Test suite for :data:`TE_REO_PREFIXES`."""

    _KEY_PREFIXES: tuple[str, ...] = (
        "te",
        "ngā",
        "nga",
        "tōku",
        "he",
        "ki",
        "kei",
        "i",
        "o",
        "a",
        "e",
        "ko",
        "ka",
        "kua",
        "me",
        "mai",
        "atu",
    )

    def test_te_reo_prefixes_contains_key_prefixes(self) -> None:
        """Check that important Te Reo prefixes are present."""
        missing = [w for w in self._KEY_PREFIXES if w not in TE_REO_PREFIXES]
        assert not missing, f"Missing prefixes: {missing}"

    def test_te_reo_prefixes_has_expected_items(self) -> None:
        """The list should contain expected number of entries roughly."""
        assert len(TE_REO_PREFIXES) >= 15  # noqa: PLR2004

    def test_te_reo_prefixes_is_list_of_strings(self) -> None:
        """Verify the type of the exported constant."""
        assert isinstance(TE_REO_PREFIXES, list)
        assert all(isinstance(w, str) for w in TE_REO_PREFIXES)


class TestBuildTokenizerExceptions:
    """Test suite for :func:`build_tokenizer_exceptions`."""

    def test_build_tokenizer_exceptions_returns_dict(self) -> None:
        """Verify the return type of the builder."""
        result = build_tokenizer_exceptions()
        assert isinstance(result, dict)

    def test_build_tokenizer_exceptions_covers_all_atoms(self) -> None:
        """Every atom in the set should have an exception rule."""
        result = build_tokenizer_exceptions()
        for atom in TE_REO_LEXICAL_ATOM_SET:
            assert atom in result, f"Missing exception for {atom!r}"

    def test_build_tokenizer_exceptions_orth_format(self) -> None:
        """Each rule should be a list containing a dict with an ORTH key."""
        result = build_tokenizer_exceptions()
        for atom, rules in result.items():
            assert isinstance(rules, list), f"Rules for {atom!r} is not a list"
            assert len(rules) == 1, f"Expected exactly one rule for {atom!r}"
            rule = rules[0]
            assert isinstance(rule, dict), f"Rule for {atom!r} is not a dict"
            assert spacy_util.ORTH in rule, f"Rule for {atom!r} missing ORTH key"
            assert rule[spacy_util.ORTH] == atom, f"Rule ORTH does not match atom {atom!r}"

    def test_build_tokenizer_exceptions_empty_is_false(self) -> None:
        """The returned dict should not be empty."""
        result = build_tokenizer_exceptions()
        assert result, "Exception dict should not be empty"


class TestCreateMaoriGuardComponent:
    """Test suite for :func:`create_maori_guard_component` and the component itself."""

    def test_create_maori_guard_component_is_callable(self) -> None:
        """The factory should return a callable."""
        nlp = spacy.blank("en")
        component = create_maori_guard_component(nlp)
        assert callable(component)

    def test_create_maori_guard_updates_tokenizer_rules(self) -> None:
        """Calling the factory should merge atoms into the tokeniser rules."""
        nlp = spacy.blank("en")
        _ = create_maori_guard_component(nlp)
        for atom in TE_REO_LEXICAL_ATOM_SET:
            assert atom in nlp.tokenizer.rules, f"Missing rule for {atom!r}"

    def test_create_maori_guard_adds_pipe(self) -> None:
        """The ``maori_guard`` component should be in the pipeline."""
        nlp = spacy.blank("en")
        _ = create_maori_guard_component(nlp)
        assert "maori_guard" in nlp.pipe_names

    def test_create_maori_guard_pipe_is_first(self) -> None:
        """The guard component should be the first in the pipeline."""
        nlp = spacy.blank("en")
        _ = create_maori_guard_component(nlp)
        assert nlp.pipe_names[0] == "maori_guard"

    def test_create_maori_guard_double_call_is_idempotent(self) -> None:
        """Calling the factory twice should not duplicate the component."""
        nlp = spacy.blank("en")
        _ = create_maori_guard_component(nlp)
        _ = create_maori_guard_component(nlp)
        assert nlp.pipe_names.count("maori_guard") == 1

    def test_maori_guard_component_returns_unchanged_doc(self) -> None:
        """The component should return the doc unchanged."""
        nlp = spacy.blank("en")
        doc = nlp("Māori")
        result_doc = _maori_guard_component(doc)
        assert doc is result_doc
