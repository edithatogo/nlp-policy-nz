"""Embedding generation for the semantic layer.

Provides dense vector embedding utilities built on Hugging Face transformer
models. Supports single-text and batched embedding generation with mean
pooling over token embeddings, and a convenience :class:`EmbeddingGenerator`
class with context-manager support.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import msgspec
import torch

from nlp_policy_nz.semantic.model_loader import load_model, unload_model

if TYPE_CHECKING:
    from transformers import AutoModel, AutoTokenizer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


class EmbeddingResult(msgspec.Struct):
    """Container for a single embedding result.

    Attributes
    ----------
    doc_id : str
        Document or chunk identifier for the embedded text.
    text : str
        The input text that was embedded.
    embedding : list[float]
        The dense vector embedding produced by the model.
    model_name : str
        Name or path of the model that generated the embedding.
    dimension : int
        Dimensionality of the embedding vector.

    """

    doc_id: str
    text: str
    embedding: list[float]
    model_name: str
    dimension: int


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------


def _mean_pooling(token_embeddings: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    """Apply mean pooling over token embeddings, ignoring padding tokens.

    Parameters
    ----------
    token_embeddings : torch.Tensor
        Shape ``(batch_size, seq_len, hidden_dim)`` — the hidden states
        from the transformer model.
    attention_mask : torch.Tensor
        Shape ``(batch_size, seq_len)`` — binary mask where ``1`` indicates
        a real token and ``0`` indicates padding.

    Returns
    -------
    torch.Tensor
        Mean-pooled embeddings of shape ``(batch_size, hidden_dim)``.

    """
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)
    sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
    return sum_embeddings / sum_mask


def generate_embedding(
    text: str,
    model: AutoModel,
    tokenizer: AutoTokenizer,
    max_length: int = 512,
) -> list[float]:
    """Generate a dense vector embedding for a single text.

    Tokenizes the input, runs it through the model, and applies mean
    pooling over token embeddings to produce a fixed-size vector.

    Parameters
    ----------
    text : str
        The input text to embed.
    model : AutoModel
        A Hugging Face transformer model (in evaluation mode).
    tokenizer : AutoTokenizer
        A Hugging Face fast tokenizer.
    max_length : int
        Maximum tokenisation length. Defaults to ``512``.

    Returns
    -------
    list[float]
        The embedding vector as a Python list of floats.

    """
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=max_length,
        use_fast=True,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    # Use the last hidden state for pooling
    token_embeddings = outputs.last_hidden_state  # (1, seq_len, hidden_dim)
    attention_mask = inputs["attention_mask"]  # (1, seq_len)

    pooled = _mean_pooling(token_embeddings, attention_mask)  # (1, hidden_dim)
    return pooled[0].tolist()


def generate_embeddings_batch(
    texts: list[str],
    model: AutoModel,
    tokenizer: AutoTokenizer,
    batch_size: int = 32,
    max_length: int = 512,
) -> list[list[float]]:
    """Generate dense vector embeddings for a list of texts in batches.

    Parameters
    ----------
    texts : list[str]
        Input texts to embed.
    model : AutoModel
        A Hugging Face transformer model (in evaluation mode).
    tokenizer : AutoTokenizer
        A Hugging Face fast tokenizer.
    batch_size : int
        Number of texts to process per batch. Defaults to ``32``.
    max_length : int
        Maximum tokenisation length per text. Defaults to ``512``.

    Returns
    -------
    list[list[float]]
        A list of embedding vectors, one per input text.

    """
    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]

        inputs = tokenizer(
            batch_texts,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=max_length,
            use_fast=True,
        )

        with torch.no_grad():
            outputs = model(**inputs)

        token_embeddings = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"]

        pooled = _mean_pooling(token_embeddings, attention_mask)
        all_embeddings.extend(pooled.tolist())

    return all_embeddings


# ---------------------------------------------------------------------------
# Convenience class
# ---------------------------------------------------------------------------


class EmbeddingGenerator:
    r"""Convenience class for generating embeddings from texts.

    Wraps model loading, embedding generation, and resource cleanup
    into a single interface with context-manager support.

    Parameters
    ----------
    model_name : str | None
        Name or path of the Hugging Face model to load. If ``None``, the
        default model from :func:`load_model` is used.
    device : str
        Device to run inference on (e.g. ``\\\"cpu\\\"``, ``\\\"cuda\\\"``).
        Defaults to ``\\\"cpu\\\"``.

    Examples
    --------
    >>> with EmbeddingGenerator() as gen:
    ...     result = gen.embed("Some policy text")
    ...     print(result.dimension)
    768

    """

    def __init__(
        self,
        model_name: str | None = None,
        device: str = "cpu",
    ) -> None:
        """Initialize the instance."""
        self._model_name = model_name
        self._device = device
        self._model: AutoModel | None = None
        self._tokenizer: AutoTokenizer | None = None
        self._loaded_name: str = ""

    # -- public properties --------------------------------------------------

    @property
    def model(self) -> AutoModel:
        """The underlying Hugging Face transformer model."""
        if self._model is None:
            raise RuntimeError("Model not loaded. Use the context manager or call load().")
        return self._model

    @property
    def tokenizer(self) -> AutoTokenizer:
        """The underlying Hugging Face fast tokenizer."""
        if self._tokenizer is None:
            raise RuntimeError("Tokenizer not loaded. Use the context manager or call load().")
        return self._tokenizer

    @property
    def model_name(self) -> str:
        """Name of the loaded model."""
        return self._loaded_name

    # -- lifecycle ----------------------------------------------------------

    def load(self) -> None:
        """Load the model and tokenizer explicitly.

        Called automatically when entering the context manager.
        """
        self._model, self._tokenizer = load_model(self._model_name)
        self._loaded_name = self._model_name or self._model.config._name_or_path  # type: ignore[union-attr]
        if self._device != "cpu":
            self._model.to(self._device)
        self._model.eval()
        logger.info(
            "EmbeddingGenerator loaded model '%s' on device '%s'",
            self._loaded_name,
            self._device,
        )

    def unload(self) -> None:
        """Release model resources explicitly.

        Called automatically when exiting the context manager.
        """
        if self._model is not None:
            unload_model(self._model)
            self._model = None
        self._tokenizer = None
        logger.info("EmbeddingGenerator resources released")

    # -- embedding methods --------------------------------------------------

    def embed(self, text: str) -> EmbeddingResult:
        """Generate an embedding for a single text.

        Parameters
        ----------
        text : str
            The input text to embed.

        Returns
        -------
        EmbeddingResult
            A struct containing the embedding vector, metadata, and model info.

        """
        embedding = generate_embedding(text, self.model, self.tokenizer)
        return EmbeddingResult(
            doc_id="",
            text=text,
            embedding=embedding,
            model_name=self._loaded_name,
            dimension=len(embedding),
        )

    def embed_batch(
        self,
        texts: list[str],
        doc_ids: list[str] | None = None,
    ) -> list[EmbeddingResult]:
        """Generate embeddings for a batch of texts.

        Parameters
        ----------
        texts : list[str]
            Input texts to embed.
        doc_ids : list[str] | None
            Optional document identifiers. If ``None``, each result receives
            an empty string as ``doc_id``.

        Returns
        -------
        list[EmbeddingResult]
            One struct per input text.

        """
        if doc_ids is None:
            doc_ids = [""] * len(texts)

        if len(doc_ids) != len(texts):
            raise ValueError(
                f"Length of doc_ids ({len(doc_ids)}) must match length of texts ({len(texts)})."
            )

        embeddings = generate_embeddings_batch(texts, self.model, self.tokenizer)
        return [
            EmbeddingResult(
                doc_id=did,
                text=txt,
                embedding=emb,
                model_name=self._loaded_name,
                dimension=len(emb),
            )
            for did, txt, emb in zip(doc_ids, texts, embeddings, strict=False)
        ]

    # -- context manager ----------------------------------------------------

    def __enter__(self) -> EmbeddingGenerator:
        """Load model resources on context entry."""
        self.load()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Release model resources on context exit."""
        self.unload()
