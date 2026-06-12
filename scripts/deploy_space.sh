#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# deploy_space.sh — Push the Gradio Space to Hugging Face Hub
#
# Uploads the contents of the spaces/ directory to a Hugging Face Space
# repository. Requires:
#   - HF_TOKEN environment variable (or --token flag)
#   - The spaces/ directory with app.py, requirements.txt, and README.md
#
# Usage:
#   bash scripts/deploy_space.sh --repo-id <user/space-name> [--token <hf-token>]
#   bash scripts/deploy_space.sh --repo-id <user/space-name> --dry-run
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SPACES_DIR="$PROJECT_ROOT/spaces"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
REPO_ID=""
TOKEN="${HF_TOKEN:-}"
DRY_RUN=false
SPACE_SDK="gradio"
COMMIT_MSG="Deploy Gradio Space to Hugging Face Hub"

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Push the nlp-policy-nz Gradio Space to Hugging Face Hub.

Options:
  --repo-id ID       Hugging Face Space repo ID (required, e.g. user/my-space)
  --token TOKEN      Hugging Face API token (default: \$HF_TOKEN env var)
  --dry-run          Validate inputs without uploading
  --sdk SDK          Space SDK type (default: gradio)
  --message MSG      Custom commit message
  -h, --help         Show this help message and exit

Environment:
  HF_TOKEN           Hugging Face API token (used if --token not provided)

Examples:
  $(basename "$0") --repo-id myuser/nz-policy-explorer
  $(basename "$0") --repo-id myuser/nz-policy-explorer --dry-run
  $(basename "$0") --repo-id myuser/nz-policy-explorer --token hf_xxxx
EOF
}

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo-id)
            REPO_ID="$2"
            shift 2
            ;;
        --token)
            TOKEN="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --sdk)
            SPACE_SDK="$2"
            shift 2
            ;;
        --message)
            COMMIT_MSG="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: Unknown option $1" >&2
            usage >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
if [[ -z "$REPO_ID" ]]; then
    echo "Error: --repo-id is required." >&2
    usage >&2
    exit 1
fi

if [[ -z "$TOKEN" ]]; then
    echo "Error: Hugging Face token not found." >&2
    echo "Set HF_TOKEN environment variable or use --token flag." >&2
    exit 1
fi

if [[ ! -d "$SPACES_DIR" ]]; then
    echo "Error: spaces/ directory not found at $SPACES_DIR" >&2
    exit 1
fi

if [[ ! -f "$SPACES_DIR/app.py" ]]; then
    echo "Error: spaces/app.py not found." >&2
    exit 1
fi

if [[ ! -f "$SPACES_DIR/requirements.txt" ]]; then
    echo "Error: spaces/requirements.txt not found." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------
if [[ "$DRY_RUN" == true ]]; then
    echo "=== DRY RUN — No files will be uploaded ==="
    echo ""
    echo "Configuration:"
    echo "  Repo ID:   $REPO_ID"
    echo "  Space SDK: $SPACE_SDK"
    echo "  Spaces dir: $SPACES_DIR"
    echo "  Commit msg: $COMMIT_MSG"
    echo ""
    echo "Files to upload:"
    ls -la "$SPACES_DIR/"
    echo ""
    echo "Validation passed. Run without --dry-run to deploy."
    exit 0
fi

# ---------------------------------------------------------------------------
# Deploy via huggingface-cli
# ---------------------------------------------------------------------------
echo "Deploying Gradio Space to $REPO_ID ..."

cd "$SPACES_DIR"

# Create or update the Space repo, then upload files
huggingface-cli repo create "$REPO_ID" \
    --type space \
    --space-sdk "$SPACE_SDK" \
    --token "$TOKEN" \
    --exist-ok

huggingface-cli upload "$REPO_ID" \
    . \
    --repo-type space \
    --token "$TOKEN" \
    --commit-message "$COMMIT_MSG"

echo ""
echo "✅ Space deployed successfully!"
echo "   https://huggingface.co/spaces/$REPO_ID"
