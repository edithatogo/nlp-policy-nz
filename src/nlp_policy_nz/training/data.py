"""Dataset preparation helpers for NZ legal NLP fine-tuning."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from nlp_policy_nz.storage import PipelineRecord, load_from_parquet

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path

TrainingTask = Literal["mlm", "citation", "deontic", "entity", "argument", "stance"]


@dataclass(frozen=True)
class TrainingExample:
    """Task-specific training example extracted from a pipeline record."""

    doc_id: str
    task: TrainingTask
    text: str
    labels: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TrainingSplitConfig:
    """Ratios and random seed used for train/validation/test splitting."""

    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1
    seed: int = 42

    def __post_init__(self) -> None:
        """Validate split ratios."""
        total = self.train_ratio + self.val_ratio + self.test_ratio
        if round(total, 8) != 1.0:
            raise ValueError("Training split ratios must sum to 1.0")
        if min(self.train_ratio, self.val_ratio, self.test_ratio) <= 0:
            raise ValueError("Training split ratios must be positive")


@dataclass(frozen=True)
class TrainingSplits:
    """Container for prepared training examples."""

    train: list[TrainingExample]
    validation: list[TrainingExample]
    test: list[TrainingExample]

    def all_examples(self) -> list[TrainingExample]:
        """Return all examples across splits."""
        return [*self.train, *self.validation, *self.test]

    def summary(self) -> dict[str, int]:
        """Return count summary for reporting and validation."""
        return {
            "train": len(self.train),
            "validation": len(self.validation),
            "test": len(self.test),
            "total_examples": len(self.all_examples()),
        }


class MaskedLanguageModelingCollator:
    """Small deterministic MLM collator for lightweight validation paths."""

    def __init__(
        self,
        *,
        mask_token_id: int,
        special_token_ids: set[int] | None = None,
        mlm_probability: float = 0.15,
        seed: int = 42,
    ) -> None:
        """Initialize the instance."""
        self.mask_token_id = mask_token_id
        self.special_token_ids = special_token_ids or set()
        self.mlm_probability = mlm_probability
        self.seed = seed

    def __call__(self, examples: Sequence[dict[str, list[int]]]) -> dict[str, list[list[int]]]:
        """Mask non-special tokens and produce MLM labels."""
        rng = random.Random(self.seed)
        input_ids: list[list[int]] = []
        attention_mask: list[list[int]] = []
        labels: list[list[int]] = []

        for example in examples:
            row = list(example["input_ids"])
            mask = list(example.get("attention_mask", [1] * len(row)))
            label_row = [-100] * len(row)
            candidate_indices = [
                index
                for index, token_id in enumerate(row)
                if token_id not in self.special_token_ids and mask[index] == 1
            ]
            selected = [
                index for index in candidate_indices if rng.random() < self.mlm_probability
            ]
            if not selected and candidate_indices:
                selected = [candidate_indices[0]]
            for index in selected:
                label_row[index] = row[index]
                row[index] = self.mask_token_id
            input_ids.append(row)
            attention_mask.append(mask)
            labels.append(label_row)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def _base_metadata(record: PipelineRecord) -> dict[str, Any]:
    """Return metadata common to examples extracted from a record."""
    return {
        "doc_id": record.doc_id,
        "corpus_source": record.corpus_source,
    }


def _is_gold_label_source(value: object) -> bool:
    """Return whether a label source denotes human/gold annotation."""
    return str(value).casefold() in {"annotated", "gold", "human", "manual"}



def build_training_examples(records: Iterable[PipelineRecord]) -> list[TrainingExample]:
    """Build task examples from pipeline records."""
    examples: list[TrainingExample] = []
    for record in records:
        metadata = _base_metadata(record)
        if record.raw_text.strip():
            examples.append(
                TrainingExample(
                    doc_id=record.doc_id,
                    task="mlm",
                    text=record.raw_text,
                    metadata=metadata,
                )
            )
        if record.nz_act_citations:
            examples.append(
                TrainingExample(
                    doc_id=record.doc_id,
                    task="citation",
                    text=record.raw_text,
                    labels={"citations": list(record.nz_act_citations)},
                    metadata=metadata,
                )
            )
        legal_effect = getattr(record, "legal_effect", None)
        deontic_modality = getattr(record, "deontic_modality", None)
        if legal_effect or deontic_modality:
            examples.append(
                TrainingExample(
                    doc_id=record.doc_id,
                    task="deontic",
                    text=record.raw_text,
                    labels={
                        "legal_effect": legal_effect,
                        "deontic_modality": deontic_modality or [],
                    },
                    metadata=metadata,
                )
            )
        if record.te_reo_terms:
            examples.append(
                TrainingExample(
                    doc_id=record.doc_id,
                    task="entity",
                    text=record.raw_text,
                    labels={"entities": list(record.te_reo_terms)},
                    metadata=metadata,
                )
            )
        arguments = getattr(record, "arguments", None) or []
        argument_label_source = getattr(record, "argument_label_source", None)
        if arguments and _is_gold_label_source(argument_label_source):
            examples.append(
                TrainingExample(
                    doc_id=record.doc_id,
                    task="argument",
                    text=record.raw_text,
                    labels={"components": [dict(item) for item in arguments]},
                    metadata={**metadata, "label_source": str(argument_label_source)},
                )
            )
        stance = getattr(record, "stance", None)
        stance_label_source = getattr(record, "stance_label_source", None)
        if stance and _is_gold_label_source(stance_label_source):
            examples.append(
                TrainingExample(
                    doc_id=record.doc_id,
                    task="stance",
                    text=record.raw_text,
                    labels={"stance": stance},
                    metadata={**metadata, "label_source": str(stance_label_source)},
                )
            )
    return examples


def _split_examples(
    examples: list[TrainingExample],
    config: TrainingSplitConfig,
) -> TrainingSplits:
    """Split examples deterministically while keeping all splits non-empty when possible."""
    shuffled = list(examples)
    random.Random(config.seed).shuffle(shuffled)
    total = len(shuffled)
    if total == 0:
        return TrainingSplits(train=[], validation=[], test=[])
    if total < 3:
        return TrainingSplits(train=shuffled, validation=[], test=[])

    train_end = max(1, int(total * config.train_ratio))
    val_count = max(1, int(total * config.val_ratio))
    test_count = max(1, total - train_end - val_count)
    if train_end + val_count + test_count > total:
        train_end = total - val_count - test_count
    val_end = train_end + val_count
    return TrainingSplits(
        train=shuffled[:train_end],
        validation=shuffled[train_end:val_end],
        test=shuffled[val_end:],
    )


def prepare_training_splits(
    parquet_paths: Sequence[str | Path],
    *,
    config: TrainingSplitConfig | None = None,
) -> TrainingSplits:
    """Load Parquet pipeline records and create train/validation/test examples."""
    split_config = config or TrainingSplitConfig()
    records: list[PipelineRecord] = []
    for path in parquet_paths:
        records.extend(load_from_parquet(path))
    return _split_examples(build_training_examples(records), split_config)


def create_mlm_collator(
    *,
    mask_token_id: int,
    special_token_ids: set[int] | None = None,
    mlm_probability: float = 0.15,
    seed: int = 42,
) -> MaskedLanguageModelingCollator:
    """Create a deterministic lightweight MLM collator."""
    return MaskedLanguageModelingCollator(
        mask_token_id=mask_token_id,
        special_token_ids=special_token_ids,
        mlm_probability=mlm_probability,
        seed=seed,
    )
