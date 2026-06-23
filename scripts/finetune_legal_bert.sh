#!/usr/bin/env bash
set -euo pipefail

# Dry-run entrypoint: emits an auditable job spec. Pass --run-training plus
# Parquet paths explicitly to start live MLM fine-tuning.
python -m nlp_policy_nz.semantic.finetune \
  --print-spec \
  --model-name nlpaueb/legal-bert-base-uncased \
  --output-dir models/legal-bert-nz \
  --batch-size 32 \
  --learning-rate 2e-5 \
  --hub-model-id nlp-policy-nz/legal-bert-nz \
  "$@"
