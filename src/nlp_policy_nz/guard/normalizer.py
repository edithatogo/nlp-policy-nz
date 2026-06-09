"""Unicode NFC normalization layer for Te Reo Māori macron handling.

Provides functions to normalise, detect, and preserve macronised characters
(ā, ē, ī, ō, ū and their uppercase forms) in Māori-language text.
All operations rely solely on the Python standard library ``unicodedata``
module — no external ML or NLP dependencies are required.
"""

import re
import unicodedata
from typing import Final

# ---------------------------------------------------------------------------
# Macron character sets
# ---------------------------------------------------------------------------
MACRON_VOWELS: Final[str] = "āēīōūĀĒĪŌŪ"
"""All macronised vowel characters (lowercase and uppercase)."""

MACRON_SET: Final[frozenset[str]] = frozenset(MACRON_VOWELS)
"""Fast membership check for any macron character."""

# ---------------------------------------------------------------------------
# Variant-to-canonical mapping
# ---------------------------------------------------------------------------
MACRON_MAP: dict[str, str] = {
    # --- common Māori words with double-vowel variants ---
    "Maaori": "Māori",
    "maori": "māori",
    "Maaoridom": "Māoridom",
    "Kaainga": "Kāinga",
    "kaainga": "kāinga",
    "Kaaawanatanga": "Kāwanatanga",
    "kawanatanga": "kāwanatanga",
    "kawana": "kāwana",
    "Whakawaa": "Whakawā",
    "whakawaa": "whakawā",
    "Whakawa": "Whakawā",
    "whakawa": "whakawā",
    "whanau": "whānau",
    "Whanau": "Whānau",
    "Pakeha": "Pākehā",
    "pakeha": "pākehā",
    "Pakehaa": "Pākehā",
    "pakehaa": "pākehā",
    "hapu": "hapū",
    "Hapu": "Hapū",
    "wahine": "wāhine",
    "Wahine": "Wāhine",
    "tane": "tāne",
    "Tane": "Tāne",
    "kaumatua": "kaumātua",
    "Kaumatua": "Kaumātua",
    "nga": "ngā",
    "Nga": "Ngā",
    "tuakana": "tuākana",
}
"""Maps common macronless or double-vowel variant spellings to their correct
NFC macronised forms.

Extend this dictionary as additional variant forms are encountered in
Māori-language corpora.
"""


# ---------------------------------------------------------------------------
# Double-vowel to macron mapping for general use
# ---------------------------------------------------------------------------
_DOUBLE_VOWEL_MACRON: Final[dict[str, str]] = {
    "aa": "ā",
    "ee": "ē",
    "ii": "ī",
    "oo": "ō",
    "uu": "ū",
    "AA": "Ā",
    "EE": "Ē",
    "II": "Ī",
    "OO": "Ō",
    "UU": "Ū",
    "Aa": "Ā",
    "Ee": "Ē",
    "Ii": "Ī",
    "Oo": "Ō",
    "Uu": "Ū",
}
"""Mapping of ASCII double-vowel sequences to their macron equivalents.

Used as a fallback for words not explicitly listed in :data:`MACRON_MAP`.
"""


def _replace_double_vowels(word: str) -> str:
    """Replace ASCII double-vowel digraphs inside *word* with macrons.

    This is applied only to words that contain no macron characters already.
    The replacement is case-aware: 'aa' -> 'ā', 'AA' -> 'Ā', 'Aa' -> 'Ā'.

    Args:
        word: A single word token to process.

    Returns:
        The word with double-vowel digraphs replaced by macron vowels.
    """
    result = list(word)
    i = 0
    while i < len(result) - 1:
        digraph = result[i] + result[i + 1]
        if digraph in _DOUBLE_VOWEL_MACRON:
            result[i] = _DOUBLE_VOWEL_MACRON[digraph]
            del result[i + 1]
        i += 1
    return "".join(result)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def normalize_text(text: str) -> str:
    """Normalise Māori-language *text* so that macrons are in NFC form.

    Performs two operations in order:

    1. Standard Unicode NFC normalisation via ``unicodedata.normalize``,
       which recomposes decomposed characters (e.g. ``'a'`` + ``COMBINING
       MACRON`` to ``'ā'``).

    2. A manual pass that replaces known double-vowel variant spellings
       (e.g. ``'Maaori'`` to ``'Māori'``) using :data:`MACRON_MAP` and a
       general double-vowel to macron substitution for common Māori words.

    Args:
        text: The raw input string, possibly containing decomposed Unicode
            macrons or double-vowel ASCII spellings.

    Returns:
        A string with all macrons in NFC composed form and common variant
        spellings corrected.

    Example:
        >>> normalize_text("Maaori kawanatanga")
        'Māori kāwanatanga'
    """
    # Step 1: NFC recomposition
    result = unicodedata.normalize("NFC", text)

    # Step 2: Apply known word-level mappings (longest keys first to
    # avoid partial replacements).
    for variant, canonical in sorted(
        MACRON_MAP.items(), key=lambda x: -len(x[0])
    ):
        pattern = re.compile(rf"\b{re.escape(variant)}\b")
        result = pattern.sub(canonical, result)

    # Step 3: For any remaining words that use double vowels, apply a
    # generic double-vowel to macron conversion.
    tokens = result.split()
    normalized_tokens: list[str] = []
    for token in tokens:
        if any(ch in MACRON_SET for ch in token):
            normalized_tokens.append(token)
        else:
            normalized_tokens.append(_replace_double_vowels(token))

    return " ".join(normalized_tokens)


def is_macronized(text: str) -> bool:
    """Return ``True`` if *text* contains any macronised vowel character.

    Checks for the presence of any of: ā, ē, ī, ō, ū (and their uppercase
    forms).

    Args:
        text: The string to inspect.

    Returns:
        ``True`` if at least one macron character is found, ``False`` if
        the string consists only of ASCII (or non-macron) characters.

    Example:
        >>> is_macronized("Māori")
        True
        >>> is_macronized("Maori")
        False
    """
    return any(ch in MACRON_SET for ch in text)


def preserve_macrons(text: str) -> str:
    """Re-normalise *text* so that any macrons survive further processing.

    Applies NFC normalisation unconditionally.  This is useful as a
    defensive step after operations (e.g. string concatenation, slice
    manipulation) that may have decomposed macron characters.

    Args:
        text: A (possibly decomposed) string.

    Returns:
        An NFC-normalised string where all macrons are in their composed
        form.

    Example:
        >>> preserve_macrons("Ma\\u0304ori")  # decomposed 'ā'
        'Māori'
    """
    return unicodedata.normalize("NFC", text)
