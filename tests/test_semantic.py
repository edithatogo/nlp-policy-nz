"""Tests for the semantic layer model loader (Track 5, Task 5.1).

Validates model-loader constants, configuration structures, and error
handling — without actually loading any models (too heavyweight for CI).
"""

from __future__ import annotations

import pytest
import torch
from types import SimpleNamespace

from nlp_policy_nz.semantic.model_loader import (
    DEFAULT_MODEL,
    DEFAULT_QUANTIZATION,
    FALLBACK_MODEL,
    ModelLoadError,
    QuantizationConfig,
    _build_bnb_config,
    _resolve_torch_dtype,
    load_model,
    unload_model,
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


class TestModelLoadingBehaviour:
    def test_resolve_torch_dtype_branches(self) -> None:
        assert _resolve_torch_dtype(None) is torch.float32
        assert _resolve_torch_dtype(SimpleNamespace(load_in_4bit=True, bnb_4bit_compute_dtype="float16")) is torch.float16
        assert _resolve_torch_dtype(SimpleNamespace(load_in_4bit=False, load_in_8bit=True)) is torch.float16
        assert _resolve_torch_dtype(SimpleNamespace(load_in_4bit=False, load_in_8bit=False)) is torch.float32

    def test_load_model_success_and_fallback(self, monkeypatch) -> None:
        calls: list[tuple[str, str]] = []

        class FakeTokenizer:
            def __init__(self, name: str) -> None:
                self.name = name

        class FakeModel:
            def __init__(self, name: str) -> None:
                self.config = SimpleNamespace(_name_or_path=name)

        def fake_tokenizer_from_pretrained(name: str, use_fast: bool = True):  # noqa: ARG001
            calls.append(("tokenizer", name))
            return FakeTokenizer(name)

        def fake_model_from_pretrained(name: str, **kwargs):
            calls.append(("model", name))
            return FakeModel(name)

        monkeypatch.setattr("nlp_policy_nz.semantic.model_loader.AutoTokenizer.from_pretrained", fake_tokenizer_from_pretrained)
        monkeypatch.setattr("nlp_policy_nz.semantic.model_loader.AutoModel.from_pretrained", fake_model_from_pretrained)

        model, tokenizer = load_model(model_name="custom/model", quantization="none", device_map="cpu")
        assert model.config._name_or_path == "custom/model"
        assert tokenizer.name == "custom/model"
        assert calls == [("tokenizer", "custom/model"), ("model", "custom/model")]

        calls.clear()

        def failing_model_from_pretrained(name: str, **kwargs):
            calls.append(("model", name))
            if name == "requested/model":
                raise RuntimeError("primary failed")
            return FakeModel(name)

        monkeypatch.setattr("nlp_policy_nz.semantic.model_loader.AutoTokenizer.from_pretrained", fake_tokenizer_from_pretrained)
        monkeypatch.setattr("nlp_policy_nz.semantic.model_loader.AutoModel.from_pretrained", failing_model_from_pretrained)

        model, tokenizer = load_model(model_name="requested/model", quantization="none", device_map="cpu")
        assert model.config._name_or_path == FALLBACK_MODEL
        assert tokenizer.name == FALLBACK_MODEL
        assert calls == [
            ("tokenizer", "requested/model"),
            ("model", "requested/model"),
            ("tokenizer", FALLBACK_MODEL),
            ("model", FALLBACK_MODEL),
        ]

    def test_load_model_failure_raises_model_load_error(self, monkeypatch) -> None:
        def failing_tokenizer(name: str, use_fast: bool = True):  # noqa: ARG001
            raise RuntimeError("tokenizer boom")

        monkeypatch.setattr("nlp_policy_nz.semantic.model_loader.AutoTokenizer.from_pretrained", failing_tokenizer)
        monkeypatch.setattr("nlp_policy_nz.semantic.model_loader.AutoModel.from_pretrained", lambda *args, **kwargs: None)

        with pytest.raises(ModelLoadError, match=f"Failed to load fallback model '{FALLBACK_MODEL}'"):
            load_model(model_name="requested/model", quantization="none", device_map="cpu")

    def test_unload_model_calls_cpu_and_clears_cache(self, monkeypatch) -> None:
        calls: dict[str, bool] = {}

        class FakeModel:
            def cpu(self) -> None:
                calls["cpu"] = True

        monkeypatch.setattr(torch.cuda, "empty_cache", lambda: calls.setdefault("empty_cache", True))

        unload_model(FakeModel())
        assert calls == {"cpu": True, "empty_cache": True}
