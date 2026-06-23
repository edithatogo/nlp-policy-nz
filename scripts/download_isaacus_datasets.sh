#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF'
Usage: scripts/download_isaacus_datasets.sh [--audit|--live]

Repo-side audit wrapper for Track 22 Isaacus dataset manifests.

  --audit  Print the local Isaacus manifest without network access (default).
  --live   Fail closed; live downloads must run in an external gated lane.
EOF
}

mode="audit"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --audit)
      mode="audit"
      ;;
    --live)
      mode="live"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf '%s\n' "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [ "$mode" = "live" ]; then
  printf '%s\n' "live mode is not available in this repo-side wrapper; use an externally approved Track 22 execution lane." >&2
  exit 64
fi

export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="${TRANSFORMERS_OFFLINE:-1}"
export WANDB_DISABLED="${WANDB_DISABLED:-true}"

printf '%s\n' "audit_mode=manifest_only network=disabled api=disabled training=disabled hub_push=disabled" >&2
PYTHONPATH="${PYTHONPATH:-src}" python -c \
  "from nlp_policy_nz.training.isaacus_adapter import render_isaacus_manifest_json; print(render_isaacus_manifest_json(), end='')"
