"""Bounded metamorphic and contract checks for issues #231-#233."""

import json
import importlib.util
from pathlib import Path

from hypothesis import given, strategies as st

from scripts.check_hardening_contracts import validate_manifest


_NORMALIZER_PATH = Path("src/nlp_policy_nz/guard/normalizer.py")
_SPEC = importlib.util.spec_from_file_location("track231_normalizer", _NORMALIZER_PATH)
assert _SPEC and _SPEC.loader
_NORMALIZER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_NORMALIZER)
normalize_text = _NORMALIZER.normalize_text


@given(st.text(max_size=256))
def test_normalization_is_idempotent(text: str) -> None:
    """Repeated normalization must not change an already-normalized value."""
    normalized = normalize_text(text)
    assert normalize_text(normalized) == normalized


def test_hardening_manifest_is_machine_readable_and_complete() -> None:
    validate_manifest()
    payload = json.loads(
        Path("data/quality/repository_hardening_manifest.json").read_text(encoding="utf-8")
    )
    assert payload["controls"]["metamorphic"]["status"] == "implemented"
    assert payload["controls"]["contract"]["status"] == "implemented"
