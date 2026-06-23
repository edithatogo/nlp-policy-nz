"""MLM fine-tuning module for domain-adapting a legal BERT model.

Provides configuration, data loading, and training orchestration for
Masked Language Model (MLM) fine-tuning on NZ legislative and Hansard text,
enabling domain adaptation of a pre-trained legal BERT model.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Final

import msgspec

from nlp_policy_nz.semantic.model_loader import DEFAULT_MODEL
from nlp_policy_nz.training.trainers import TrainingJobSpec, create_legal_bert_mlm_job

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_OUTPUT_DIR: Final[str] = "./models/nz-legal-bert"
"""Default local output directory for saving fine-tuned models."""

DEFAULT_MAX_LENGTH: Final[int] = 128
"""Default maximum token-sequence length for tokenization."""

DEFAULT_BATCH_SIZE: Final[int] = 16
"""Default per-device batch size for training."""

DEFAULT_LEARNING_RATE: Final[float] = 2e-5
"""Default peak learning rate for the AdamW optimiser."""

DEFAULT_NUM_EPOCHS: Final[int] = 3
"""Default number of training epochs."""

DEFAULT_WARMUP_RATIO: Final[float] = 0.1
"""Default fraction of total training steps used for linear warmup."""


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class FineTuneConfig(msgspec.Struct):
    """Configuration for MLM fine-tuning.

    Attributes
    ----------
    model_name : str
        Hugging Face model name or local path to initialise from.
        Defaults to ``"nlpaueb/legal-bert-base-uncased"``.
    output_dir : str
        Directory where the fine-tuned model and tokenizer are saved.
        Defaults to ``"./models/nz-legal-bert"``.
    max_length : int
        Maximum sequence length (in tokens) for tokenization.
        Defaults to ``128``.
    batch_size : int
        Per-device batch size for training.
        Defaults to ``16``.
    learning_rate : float
        Peak learning rate for the optimiser.
        Defaults to ``2e-5``.
    num_epochs : int
        Number of training epochs.
        Defaults to ``3``.
    warmup_ratio : float
        Fraction of training steps used for linear LR warmup.
        Defaults to ``0.1``.
    push_to_hub : bool
        Whether to push the fine-tuned model to the Hugging Face Hub.
        Defaults to ``False``.
    hub_model_id : str
        Repository ID on the Hugging Face Hub when ``push_to_hub`` is
        ``True`` (e.g. ``"my-org/nz-legal-bert"``).
        Defaults to ``""``.

    """

    model_name: str = DEFAULT_MODEL
    output_dir: str = DEFAULT_OUTPUT_DIR
    max_length: int = DEFAULT_MAX_LENGTH
    batch_size: int = DEFAULT_BATCH_SIZE
    learning_rate: float = DEFAULT_LEARNING_RATE
    num_epochs: int = DEFAULT_NUM_EPOCHS
    warmup_ratio: float = DEFAULT_WARMUP_RATIO
    push_to_hub: bool = False
    hub_model_id: str = ""


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_training_data(parquet_paths: list[str], max_length: int = DEFAULT_MAX_LENGTH) -> object:
    """Load Parquet files, extract ``raw_text``, and tokenize for MLM.

    Parameters
    ----------
    parquet_paths : list[str]
        One or more paths to Parquet files containing a ``raw_text`` column
        with legislative or Hansard text.
    max_length : int
        Maximum token sequence length. Defaults to ``128``.

    Returns
    -------
    Dataset
        A Hugging Face ``Dataset`` with tokenized ``input_ids`` and
        ``attention_mask`` columns, ready for MLM training.

    Raises
    ------
    FileNotFoundError
        If any of the provided Parquet paths do not exist.
    ValueError
        If none of the Parquet files contain a ``raw_text`` column.

    """
    missing = [p for p in parquet_paths if not Path(p).exists()]
    if missing:
        raise FileNotFoundError(f"Parquet file(s) not found: {missing}")

    from datasets import load_dataset  # noqa: PLC0415
    from transformers import AutoTokenizer  # noqa: PLC0415

    logger.info("Loading Parquet files: %s", parquet_paths)
    dataset = load_dataset("parquet", data_files=parquet_paths, split="train")

    if "raw_text" not in dataset.column_names:
        raise ValueError(
            "Parquet files must contain a 'raw_text' column. "
            f"Available columns: {dataset.column_names}"
        )

    logger.info("Loaded %d rows from Parquet. Tokenizing ...", len(dataset))
    tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL, use_fast=True)

    def _tokenize_fn(batch: dict) -> dict:
        return tokenizer(
            batch["raw_text"],
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_special_tokens_mask=True,
        )

    dataset = dataset.map(
        _tokenize_fn,
        batched=True,
        remove_columns=[
            c
            for c in dataset.column_names
            if c not in ("input_ids", "attention_mask", "special_tokens_mask")
        ],
        desc="Tokenizing",
    )

    logger.info("Tokenization complete. Dataset size: %d examples.", len(dataset))
    return dataset


def build_mlm_job_spec(config: FineTuneConfig) -> TrainingJobSpec:
    """Build a serializable Track 20 Legal-BERT MLM job specification."""
    job = create_legal_bert_mlm_job(
        output_dir=config.output_dir,
        hub_model_id=config.hub_model_id or "nlp-policy-nz/legal-bert-nz",
    )
    return TrainingJobSpec(
        task=job.task,
        model=type(job.model)(
            model_name=config.model_name,
            output_dir=config.output_dir,
            tokenizer_name=job.model.tokenizer_name,
            trust_remote_code=job.model.trust_remote_code,
        ),
        training=type(job.training)(
            max_steps=job.training.max_steps,
            num_epochs=config.num_epochs,
            per_device_batch_size=config.batch_size,
            learning_rate=config.learning_rate,
            max_length=config.max_length,
            warmup_ratio=config.warmup_ratio,
            gradient_accumulation_steps=job.training.gradient_accumulation_steps,
            report_to=job.training.report_to,
        ),
        qlora=job.qlora,
        dataset_split_dir=job.dataset_split_dir,
        hub_model_id=config.hub_model_id or job.hub_model_id,
    )


def build_dry_run_payload(config: FineTuneConfig, parquet_paths: list[str]) -> dict[str, object]:
    """Return auditable dry-run evidence without loading models or datasets."""
    return {
        "surface": "nlp_policy_nz.semantic.finetune",
        "mode": "dry_run",
        "training_started": False,
        "model_download_started": False,
        "hub_push_started": False,
        "parquet_paths": parquet_paths,
        "job_spec": build_mlm_job_spec(config).to_dict(),
        "external_gates": [
            "Explicit --run-training opt-in",
            "Readable Parquet files containing raw_text",
            "Installed datasets/transformers/torch runtime",
            "CUDA/GPU validation for production-scale runs",
            "Hugging Face authentication when --push-to-hub is used",
        ],
    }

# ---------------------------------------------------------------------------
# Fine-tuning
# ---------------------------------------------------------------------------


def finetune_model(config: FineTuneConfig, parquet_paths: list[str]) -> str:
    """Run MLM fine-tuning on NZ legislative/Hansard text.

    Parameters
    ----------
    config : FineTuneConfig
        Configuration object controlling model, training hyper-parameters,
        and output behaviour.
    parquet_paths : list[str]
        One or more paths to Parquet files with a ``raw_text`` column.

    Returns
    -------
    str
        Absolute path to the directory where the fine-tuned model and
        tokenizer have been saved.

    """
    import torch  # noqa: PLC0415
    from transformers import (  # noqa: PLC0415
        AutoModelForMaskedLM,
        AutoTokenizer,
        DataCollatorForLanguageModeling,
        Trainer,
        TrainingArguments,
    )

    # --- data ---
    dataset = load_training_data(parquet_paths, max_length=config.max_length)

    # --- model & tokenizer ---
    logger.info("Loading model: %s", config.model_name)
    tokenizer = AutoTokenizer.from_pretrained(config.model_name, use_fast=True)
    model = AutoModelForMaskedLM.from_pretrained(config.model_name)

    # --- data collator (dynamic masking) ---
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=True,
        mlm_probability=0.15,
    )

    # --- training arguments ---
    hub_args: dict = {}
    if config.push_to_hub and config.hub_model_id:
        hub_args["hub_model_id"] = config.hub_model_id
        hub_args["push_to_hub"] = True

    training_args = TrainingArguments(
        output_dir=config.output_dir,
        overwrite_output_dir=True,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_dir=str(Path(config.output_dir) / "logs"),
        logging_steps=50,
        save_steps=500,
        save_total_limit=2,
        dataloader_num_workers=0,  # avoid multiprocessing issues on Windows
        fp16=torch.cuda.is_available(),
        report_to="none",
        **hub_args,
    )

    # --- trainer ---
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    # --- train ---
    logger.info("Starting MLM fine-tuning for %d epoch(s) ...", config.num_epochs)
    trainer.train()

    # --- save ---
    output_path = str(Path(config.output_dir).resolve())
    logger.info("Saving model to: %s", output_path)
    trainer.save_model(output_path)
    tokenizer.save_pretrained(output_path)

    # --- optional hub push ---
    if config.push_to_hub and config.hub_model_id:
        logger.info("Pushing model to Hub: %s", config.hub_model_id)
        trainer.push_to_hub()

    logger.info("Fine-tuning complete.")
    return output_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the fine-tuning script."""
    parser = argparse.ArgumentParser(
        description=(
            "Build an auditable Legal-BERT MLM fine-tuning job spec. "
            "Training only starts when --run-training is supplied."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "parquet_paths",
        nargs="*",
        help=(
            "One or more Parquet file paths containing a 'raw_text' column. "
            "Required only with --run-training."
        ),
    )

    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL,
        help="Pre-trained model name or local path to start from.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to save the fine-tuned model.",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=DEFAULT_MAX_LENGTH,
        help="Maximum token sequence length.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Per-device training batch size.",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=DEFAULT_LEARNING_RATE,
        help="Peak learning rate.",
    )
    parser.add_argument(
        "--num-epochs",
        type=int,
        default=DEFAULT_NUM_EPOCHS,
        help="Number of training epochs.",
    )
    parser.add_argument(
        "--warmup-ratio",
        type=float,
        default=DEFAULT_WARMUP_RATIO,
        help="Fraction of steps for linear LR warmup.",
    )
    parser.add_argument(
        "--push-to-hub",
        action="store_true",
        help="Push the fine-tuned model to the Hugging Face Hub. Requires --run-training.",
    )
    parser.add_argument(
        "--hub-model-id",
        default="",
        help="Hub repository ID (e.g. 'my-org/nz-legal-bert'). Required when --push-to-hub is set.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging.",
    )
    parser.add_argument(
        "--print-spec",
        action="store_true",
        help="Print the dry-run job spec JSON and exit. This is the default unless --run-training is set.",
    )
    parser.add_argument(
        "--spec-output",
        help="Optional path where dry-run job spec JSON should be written.",
    )
    parser.add_argument(
        "--run-training",
        action="store_true",
        help="Explicitly start live MLM fine-tuning. Without this flag the CLI is dry-run only.",
    )

    return parser.parse_args(argv)


def _main(argv: list[str] | None = None) -> None:
    """CLI entry point for ``python -m nlp_policy_nz.semantic.finetune``."""
    args = _parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )

    config = FineTuneConfig(
        model_name=args.model_name,
        output_dir=args.output_dir,
        max_length=args.max_length,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        num_epochs=args.num_epochs,
        warmup_ratio=args.warmup_ratio,
        push_to_hub=args.push_to_hub,
        hub_model_id=args.hub_model_id,
    )

    if not args.run_training:
        payload = build_dry_run_payload(config, args.parquet_paths)
        rendered = json.dumps(payload, indent=2, sort_keys=True)
        if args.spec_output:
            out_p = Path(args.spec_output)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(f"{rendered}\n", encoding="utf-8")
        if args.print_spec or not args.spec_output:
            sys.stdout.write(f"{rendered}\n")
        return

    if not args.parquet_paths:
        raise SystemExit("--run-training requires at least one Parquet path.")

    _ = finetune_model(config, args.parquet_paths)


if __name__ == "__main__":
    _main()
