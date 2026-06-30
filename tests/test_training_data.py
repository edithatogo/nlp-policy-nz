"""Tests for Track 20 training data preparation helpers."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from nlp_policy_nz.storage import PipelineRecord, serialize_to_parquet
from nlp_policy_nz.training.data import (
    TrainingSplitConfig,
    build_training_examples,
    create_mlm_collator,
    prepare_training_splits,
)


def _records() -> list[PipelineRecord]:
    """Return small records covering the Track 20 supervised task mix."""
    return [
        PipelineRecord(
            doc_id="doc-1",
            corpus_source="legislation",
            raw_text="The Minister must consult section 7 of the Act.",
            cleaned_tokens=["The", "Minister", "must", "consult"],
            nz_act_citations=["section 7 of the Act"],
            te_reo_terms=["Aotearoa"],
            deontic_modality=[{"modality": "obligation", "cue": "must"}],
            legal_effect="obligation",
        ),
        PipelineRecord(
            doc_id="doc-2",
            corpus_source="hansard",
            raw_text="The member may table a report about Wellington.",
            cleaned_tokens=["The", "member", "may", "table"],
            nz_act_citations=[],
            te_reo_terms=["Wellington"],
            legal_effect="permission",
        ),
        PipelineRecord(
            doc_id="doc-3",
            corpus_source="legislation",
            raw_text="No person must obstruct Te Tiriti compliance.",
            cleaned_tokens=["No", "person", "must", "obstruct"],
            nz_act_citations=["Te Tiriti clause"],
            te_reo_terms=["Te Tiriti"],
            legal_effect="prohibition",
        ),
    ]


def test_build_training_examples_extracts_task_specific_records() -> None:
    """Records are converted into MLM, citation, deontic, and entity tasks."""
    examples = build_training_examples(_records())

    tasks = [example.task for example in examples]
    assert tasks.count("mlm") == 3
    assert tasks.count("citation") == 2
    assert tasks.count("deontic") == 3
    assert tasks.count("entity") == 3
    citation = next(example for example in examples if example.task == "citation")
    assert citation.labels["citations"] == ["section 7 of the Act"]
    assert citation.metadata["doc_id"] == "doc-1"


def test_prepare_training_splits_from_parquet_is_deterministic() -> None:
    """Parquet corpora produce deterministic train/validation/test splits."""
    tmp_path = Path(".tmp") / "training-data-tests" / uuid4().hex
    tmp_path.mkdir(parents=True, exist_ok=True)
    parquet = tmp_path / "records.parquet"
    serialize_to_parquet(_records(), parquet)
    config = TrainingSplitConfig(train_ratio=0.5, val_ratio=0.25, test_ratio=0.25, seed=7)

    first = prepare_training_splits([parquet], config=config)
    second = prepare_training_splits([parquet], config=config)

    assert [example.doc_id for example in first.train] == [
        example.doc_id for example in second.train
    ]
    assert len(first.train) > 0
    assert len(first.validation) > 0
    assert len(first.test) > 0
    assert first.summary()["total_examples"] == len(first.all_examples())


def test_split_config_rejects_invalid_ratios() -> None:
    """Split ratios must be positive and sum to one."""
    with pytest.raises(ValueError, match=r"sum to 1\.0"):
        TrainingSplitConfig(train_ratio=0.9, val_ratio=0.2, test_ratio=0.1)


def test_prepare_training_splits_handles_empty_parquet_list() -> None:
    """Empty corpus inputs produce empty split containers."""
    splits = prepare_training_splits([])

    assert splits.summary() == {
        "train": 0,
        "validation": 0,
        "test": 0,
        "total_examples": 0,
    }


def test_mlm_collator_masks_non_special_tokens_deterministically() -> None:
    """The lightweight MLM collator masks a deterministic token subset."""
    collator = create_mlm_collator(mask_token_id=103, special_token_ids={101, 102}, seed=4)
    batch = collator(
        [
            {"input_ids": [101, 11, 12, 13, 102], "attention_mask": [1, 1, 1, 1, 1]},
            {"input_ids": [101, 21, 22, 23, 102], "attention_mask": [1, 1, 1, 1, 1]},
        ]
    )

    assert len(batch["input_ids"]) == 2
    assert batch["input_ids"][0][0] == 101
    assert batch["input_ids"][0][-1] == 102
    assert any(label != -100 for row in batch["labels"] for label in row)
    assert all(row[0] == -100 and row[-1] == -100 for row in batch["labels"])
