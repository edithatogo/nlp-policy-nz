"""Quantized model loader for the semantic layer.

Provides loading and unloading of transformer models with bitsandbytes
quantization, supporting 4-bit and 8-bit precision for memory-efficient
inference on local hardware.
"""

from __future__ import annotations

import logging
from typing import Final

import torch
from msgspec import Struct
from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MODEL: Final[str] = "nlpaueb/legal-bert-base-uncased"
"""Default legal-domain BERT model used for semantic analysis."""

FALLBACK_MODEL: Final[str] = "bert-base-uncased"
"""Fallback general-purpose BERT model when the primary model is unavailable."""

DEFAULT_QUANTIZATION: Final[str] = "4bit"
"""Default quantization precision (``\"4bit\"`` or ``\"8bit\"``)."""


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ModelLoadError(Exception):
    """Raised when a model cannot be loaded from Hugging Face or locally."""


# ---------------------------------------------------------------------------
# Quantization configuration
# ---------------------------------------------------------------------------


class QuantizationConfig(Struct, frozen=True):
    """Bitsandbytes quantization parameters for model loading.

    Attributes
    ----------
    load_in_4bit : bool
        Whether to load the model in 4-bit precision. Defaults to ``True``.
    bnb_4bit_compute_dtype : str
        Computation dtype for 4-bit layers (e.g. ``\"float16\"``, ``\"bfloat16\"``).
        Defaults to ``\"float16\"``.
    bnb_4bit_use_double_quant : bool
        Enable double quantization for additional memory savings.
        Defaults to ``True``.
    bnb_4bit_quant_type : str
        Quantization type; ``\"nf4\"`` (normalised float 4) or ``\"fp4\"``.
        Defaults to ``\"nf4\"``.

    """

    load_in_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_use_double_quant: bool = True
    bnb_4bit_quant_type: str = "nf4"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_model(
    model_name: str | None = None,
    quantization: str = "4bit",
    device_map: str = "auto",
) -> tuple[AutoModel, AutoTokenizer]:
    """Load a Hugging Face model with optional bitsandbytes quantization.

    Parameters
    ----------
    model_name : str | None
        Name or path of the model to load. If ``None``, the value of
        :data:`DEFAULT_MODEL` is used.
    quantization : str
        Quantisation mode — ``\"4bit\"``, ``\"8bit\"``, or ``\"none\"``.
        Defaults to ``\"4bit\"``.
    device_map : str
        Device placement strategy passed to ``from_pretrained``.
        Defaults to ``\"auto\"``.

    Returns
    -------
    tuple[AutoModel, AutoTokenizer]
        A ``(model, tokenizer)`` pair ready for inference.

    Raises
    ------
    ModelLoadError
        If both the requested model and the fallback model fail to load.

    Examples
    --------
    >>> model, tokenizer = load_model()
    >>> model, tokenizer = load_model("bert-base-uncased", quantization="none")

    """
    model_name = model_name or DEFAULT_MODEL
    quant_config = _build_bnb_config(quantization)

    # --- attempt loading the requested model ---
    try:
        logger.info("Loading model: %s (quantization=%s)", model_name, quantization)
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        model = AutoModel.from_pretrained(
            model_name,
            quantization_config=quant_config,
            device_map=device_map,
            torch_dtype=_resolve_torch_dtype(quant_config),
        )
        return model, tokenizer
    except Exception as exc:
        logger.warning(
            "Failed to load model '%s': %s. Attempting fallback to '%s'.",
            model_name,
            exc,
            FALLBACK_MODEL,
        )

    # --- fallback ---
    try:
        tokenizer = AutoTokenizer.from_pretrained(FALLBACK_MODEL, use_fast=True)
        model = AutoModel.from_pretrained(
            FALLBACK_MODEL,
            quantization_config=quant_config,
            device_map=device_map,
            torch_dtype=_resolve_torch_dtype(quant_config),
        )
        return model, tokenizer
    except Exception as exc:
        raise ModelLoadError(f"Failed to load fallback model '{FALLBACK_MODEL}': {exc}") from exc


def unload_model(model: torch.nn.Module) -> None:
    """Release a loaded model from GPU memory.

    Moves the model to the CPU, deletes its references, and runs the
    garbage collector to free GPU memory.

    Parameters
    ----------
    model : torch.nn.Module
        The PyTorch model to unload.

    Examples
    --------
    >>> model, tokenizer = load_model()
    >>> unload_model(model)

    """
    try:
        model.cpu()
    except Exception:  # model may not have .cpu()
        pass
    finally:
        del model
        torch.cuda.empty_cache()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_bnb_config(quantization: str) -> BitsAndBytesConfig | None:
    """Construct a :class:`BitsAndBytesConfig` from a short-hand string.

    Returns ``None`` when ``quantization`` is ``\"none\"``.
    """
    if quantization == "4bit":
        cfg = QuantizationConfig()
        return BitsAndBytesConfig(
            load_in_4bit=cfg.load_in_4bit,
            bnb_4bit_compute_dtype=cfg.bnb_4bit_compute_dtype,
            bnb_4bit_use_double_quant=cfg.bnb_4bit_use_double_quant,
            bnb_4bit_quant_type=cfg.bnb_4bit_quant_type,
        )
    if quantization == "8bit":
        return BitsAndBytesConfig(load_in_8bit=True)
    if quantization == "none":
        return None
    raise ValueError(
        f"Unsupported quantization value: '{quantization}'. Expected one of '4bit', '8bit', 'none'."
    )


def _resolve_torch_dtype(config: BitsAndBytesConfig | None) -> torch.dtype:
    """Resolve the compute :class:`torch.dtype` from a configuration.

    Defaults to :class:`torch.float32` when ``config`` is ``None``.
    """
    if config is None:
        return torch.float32
    if config.load_in_4bit and hasattr(config, "bnb_4bit_compute_dtype"):
        dtype_str = config.bnb_4bit_compute_dtype
    elif config.load_in_8bit:
        return torch.float16
    else:
        return torch.float32
    return getattr(torch, dtype_str, torch.float16)
