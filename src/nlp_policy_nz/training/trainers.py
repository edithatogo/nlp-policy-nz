"""Training job specifications for Track 20 fine-tuning workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

TrainingTaskName = Literal[
    "mlm", "citation", "deontic", "entity", "argument", "stance", "qa", "maori"
]


@dataclass(frozen=True)
class ModelTrainingConfig:
    """Model and output configuration for a fine-tuning job."""

    model_name: str
    output_dir: str
    tokenizer_name: str | None = None
    trust_remote_code: bool = False


@dataclass(frozen=True)
class TrainingHyperparameters:
    """Common training hyperparameters for model adaptation jobs."""

    max_steps: int | None = None
    num_epochs: float | None = 3.0
    per_device_batch_size: int = 8
    learning_rate: float = 2e-5
    max_length: int = 512
    warmup_ratio: float = 0.1
    gradient_accumulation_steps: int = 1
    report_to: str = "wandb"


@dataclass(frozen=True)
class QLoRAConfig:
    """QLoRA adapter and quantization configuration."""

    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: tuple[str, ...] = ("all-linear",)
    load_in_4bit: bool = True
    quant_type: str = "nf4"
    compute_dtype: str = "bfloat16"


@dataclass(frozen=True)
class TrainingJobSpec:
    """Serializable specification for a planned fine-tuning run."""

    task: TrainingTaskName
    model: ModelTrainingConfig
    training: TrainingHyperparameters = TrainingHyperparameters()
    qlora: QLoRAConfig | None = None
    dataset_split_dir: str | None = None
    hub_model_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible dictionary."""
        return asdict(self)


def create_legal_bert_mlm_job(
    *,
    output_dir: str,
    hub_model_id: str = "nlp-policy-nz/legal-bert-nz",
) -> TrainingJobSpec:
    """Create the Track 20 Legal-BERT MLM fine-tuning job spec."""
    return TrainingJobSpec(
        task="mlm",
        model=ModelTrainingConfig(
            model_name="nlpaueb/legal-bert-base-uncased",
            output_dir=output_dir,
        ),
        training=TrainingHyperparameters(
            max_steps=100_000,
            num_epochs=None,
            per_device_batch_size=32,
            learning_rate=2e-5,
            max_length=512,
            report_to="wandb",
        ),
        hub_model_id=hub_model_id,
    )


def create_qlora_job(
    *,
    model_name: str,
    task: TrainingTaskName,
    output_dir: str,
    hub_model_id: str,
    qlora: QLoRAConfig | None = None,
    training: TrainingHyperparameters | None = None,
) -> TrainingJobSpec:
    """Create a QLoRA fine-tuning job spec for a large model."""
    return TrainingJobSpec(
        task=task,
        model=ModelTrainingConfig(
            model_name=model_name,
            output_dir=output_dir,
            trust_remote_code=True,
        ),
        training=training
        or TrainingHyperparameters(
            per_device_batch_size=1,
            gradient_accumulation_steps=16,
            learning_rate=2e-4,
            report_to="wandb",
        ),
        qlora=qlora or QLoRAConfig(),
        hub_model_id=hub_model_id,
    )


def create_legal_bert_argument_component_job(
    *,
    dataset_split_dir: str,
    output_dir: str,
    hub_model_id: str = "nlp-policy-nz/legal-bert-argument-components",
) -> TrainingJobSpec:
    """Create the Track 13 Legal-BERT argument component fine-tuning job spec."""
    return TrainingJobSpec(
        task="argument",
        model=ModelTrainingConfig(
            model_name="nlpaueb/legal-bert-base-uncased",
            output_dir=output_dir,
        ),
        training=TrainingHyperparameters(
            num_epochs=5.0,
            per_device_batch_size=16,
            learning_rate=2e-5,
            max_length=512,
            report_to="wandb",
        ),
        dataset_split_dir=dataset_split_dir,
        hub_model_id=hub_model_id,
    )


def create_legal_bert_stance_job(
    *,
    dataset_split_dir: str,
    output_dir: str,
    hub_model_id: str = "nlp-policy-nz/legal-bert-stance",
) -> TrainingJobSpec:
    """Create the Track 13 Legal-BERT stance classification fine-tuning job spec."""
    return TrainingJobSpec(
        task="stance",
        model=ModelTrainingConfig(
            model_name="nlpaueb/legal-bert-base-uncased",
            output_dir=output_dir,
        ),
        training=TrainingHyperparameters(
            num_epochs=5.0,
            per_device_batch_size=16,
            learning_rate=2e-5,
            max_length=512,
            report_to="wandb",
        ),
        dataset_split_dir=dataset_split_dir,
        hub_model_id=hub_model_id,
    )
