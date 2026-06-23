#!/usr/bin/env sh
set -eu

mode="audit"
if [ "${1:-}" = "--audit" ]; then
  shift
elif [ "${1:-}" = "--live" ]; then
  printf '%s\n' "Live MoR evaluation is intentionally disabled in this repo-side audit wrapper." >&2
  printf '%s\n' "Run external clone/download/train workflows only from a separate, reviewed live lane." >&2
  exit 64
fi

export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"
export WANDB_DISABLED="${WANDB_DISABLED:-true}"

printf '%s\n' "track21 architecture audit: mor (${mode}); no clone, download, training, or Hub push will be started." >&2

PYTHONPATH="${PYTHONPATH:-src}" python -c 'from nlp_policy_nz.training.eval_arch import main; raise SystemExit(main())' \
  --example-report \
  --architecture mor \
  "$@"
