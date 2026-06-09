"""Tests for the semantic layer model loader (Track 5, Task 5.1).

Validates model-loader constants, configuration structures, and error
handling — without actually loading any models (too heavyweight for CI).
"""

from __future__ import annotations

import pytest

from nlp_policy_nz.semantic.model_loader import (
    DEFAULT_MODEL,
    DEFAULT_QUANTIZATION,
    FALLBACK_MODEL,
    ModelLoadError,
    QuantizationConfig,
    _build_bnb_config,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    """Verify the public-facing module constants."""

    def test_default_model_constant(self) -> None:
        """Default model should be the Legal-BERT uncased variant."""
        assert DEFAULT_MODEL == "nlpaueb/legal-bert-base-uncased"

    def test_fallback_model_constant(self) -> None:
        """Fallback model should be the general-purpose BERT uncased."""
        assert FALLBACK_MODEL == "bert-base-uncased"

    def test_default_quantization_constant(self) -> None:
        """Default quantization mode should be ``\"4bit\"``."""
        assert DEFAULT_QUANTIZATION == "4bit"


# ---------------------------------------------------------------------------
# QuantizationConfig
# ---------------------------------------------------------------------------


class TestQuantizationConfig:
    """Validate the ``QuantizationConfig`` msgspec struct."""

    def test_default_instantiation(self) -> None:
        """Default config should enable 4-bit with nf4 and double quant."""
        cfg = QuantizationConfig()
        assert cfg.load_in_4bit is True
        assert cfg.bnb_4bit_compute_dtype == "float16"
        assert cfg.bnb_4bit_use_double_quant is True
        assert cfg.bnb_4bit_quant_type == "nf4"

    def test_custom_values(self) -> None:
        """Overriding fields should produce the expected config."""
        cfg = QuantizationConfig(
            load_in_4bit=False,
            bnb_4bit_compute_dtype="bfloat16",
            bnb_4bit_use_double_quant=False,
            bnb_4bit_quant_type="fp4",
        )
        assert cfg.load_in_4bit is False
        assert cfg.bnb_4bit_compute_dtype == "bfloat16"
        assert cfg.bnb_4bit_use_double_quant is False
        assert cfg.bnb_4bit_quant_type == "fp4"

    def test_is_frozen(self) -> None:
        """Struct is frozen (immutable) after creation."""
        cfg = QuantizationConfig()
        with pytest.raises(AttributeError):
            cfg.load_in_4bit = False  # type: ignore[misc]

    def test_repr(self) -> None:
        """String representation should be informative."""
        cfg = QuantizationConfig()
        assert "QuantizationConfig" in repr(cfg)
        assert "load_in_4bit=True" in repr(cfg)
        assert "bnb_4bit_quant_type='nf4'" in repr(cfg)


# ---------------------------------------------------------------------------
# _build_bnb_config (internal helper)
# ---------------------------------------------------------------------------


class TestBuildBnbConfig:
    """Validate the internal ``_build_bnb_config`` helper."""

    def test_4bit_config(self) -> None:
        """``\"4bit\"`` should produce a config with ``load_in_4bit=True``."""
        cfg = _build_bnb_config("4bit")
        assert cfg is not None
        assert cfg.load_in_4bit is True

    def test_8bit_config(self) -> None:
        """``\"8bit\"`` should produce a config with ``load_in_8bit=True``."""
        cfg = _build_bnb_config("8bit")
        assert cfg is not None
        assert cfg.load_in_8bit is True

    def test_none_config(self) -> None:
        """``\"none\"`` should return ``None``."""
        cfg = _build_bnb_config("none")
        assert cfg is None

    def test_invalid_quantization_raises_value_error(self) -> None:
        """An unsupported quantization string raises ``ValueError``."""
        with pytest.raises(ValueError, match="Unsupported quantization"):
            _build_bnb_config("invalid")


# ---------------------------------------------------------------------------
# ModelLoadError
# ---------------------------------------------------------------------------


class TestModelLoadError:
    """Validate the custom ``ModelLoadError`` exception."""

    def test_is_exception(self) -> None:
        """``ModelLoadError`` should be a subclass of ``Exception``."""
        assert issubclass(ModelLoadError, Exception)

    def test_can_be_raised_with_message(self) -> None:
        """Raising ``ModelLoadError`` with a message should work."""
        msg = "Failed to load model"
        with pytest.raises(ModelLoadError, match=msg):
            raise ModelLoadError(msg)
