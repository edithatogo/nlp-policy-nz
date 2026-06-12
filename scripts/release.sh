#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# release.sh ? Create a versioned release archive and optionally publish to Zenodo
#
# Bundles a Parquet file with metadata into a .tar.gz archive and publishes
# it to the Zenodo Sandbox (default) or Zenodo Production.
#
# Usage:
#   bash scripts/release.sh --parquet <file> --version <ver> --title <t> --description <d> --creators <json>
#   bash scripts/release.sh --parquet <file> --version <ver> --title <t> --description <d> --creators <json> --environment production
#   bash scripts/release.sh --parquet <file> --version <ver> --title <t> --description <d> --creators <json> --dry-run
#   bash scripts/release.sh --help
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
PARQUET_FILE=""
VERSION=""
TITLE=""
DESCRIPTION=""
CREATORS=""
ENVIRONMENT="sandbox"
OUTPUT_DIR=""
DRY_RUN=false

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Create a versioned release archive and optionally publish to Zenodo.

Options:
  --parquet PATH    Path to the Parquet file to release (required)
  --version VER     Semantic version string, e.g. "1.0.0" (required)
  --title TITLE     Title for the Zenodo deposit (required)
  --description DESC Description for the Zenodo deposit (required)
  --creators JSON   JSON list of creator dicts (required, e.g. '[{"name": "Doe, Jane"}]')
  --environment ENV Zenodo environment: "sandbox" (default) or "production"
  --output-dir DIR  Directory for the local archive (default: temporary directory)
  --dry-run         Validate inputs without publishing
  -h, --help        Show this help message and exit

Environment:
  ZENODO_SANDBOX_TOKEN      Zenodo Sandbox API token (required when --environment sandbox)
  ZENODO_PRODUCTION_TOKEN   Zenodo Production API token (required when --environment production)

Examples:
  $(basename "$0") --parquet output/legislation.parquet --version 1.0.0 --title "NZ Legislation v1.0" --description "Preprocessed NZ legislation corpus" --creators '[{"name": "Doe, Jane"}]'
  $(basename "$0") --parquet output/hansard.parquet --version 2.1.0 --title "Hansard v2.1" --description "Preprocessed Hansard corpus" --creators '[{"name": "Smith, John"}]' --dry-run
  $(basename "$0") --parquet output/data.parquet --version 1.0.0 --title "Release" --description "Release description" --creators '[{"name": "Author"}]' --environment production
EOF
}


# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --parquet)
            PARQUET_FILE="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --title)
            TITLE="$2"
            shift 2
            ;;
        --description)
            DESCRIPTION="$2"
            shift 2
            ;;
        --creators)
            CREATORS="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
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
if [[ -z "$PARQUET_FILE" ]]; then
    echo "Error: --parquet is required." >&2
    usage >&2
    exit 1
fi

if [[ ! -f "$PARQUET_FILE" ]]; then
    echo "Error: Parquet file not found: $PARQUET_FILE" >&2
    exit 1
fi

if [[ -z "$VERSION" ]]; then
    echo "Error: --version is required." >&2
    usage >&2
    exit 1
fi

if [[ -z "$TITLE" ]]; then
    echo "Error: --title is required." >&2
    usage >&2
    exit 1
fi

if [[ -z "$DESCRIPTION" ]]; then
    echo "Error: --description is required." >&2
    usage >&2
    exit 1
fi

if [[ -z "$CREATORS" ]]; then
    echo "Error: --creators is required." >&2
    usage >&2
    exit 1
fi

if [[ "$ENVIRONMENT" != "sandbox" && "$ENVIRONMENT" != "production" ]]; then
    echo "Error: --environment must be 'sandbox' or 'production' (got: $ENVIRONMENT)" >&2
    exit 1
fi

# Resolve the expected token environment variable
if [[ "$ENVIRONMENT" == "sandbox" ]]; then
    TOKEN_VAR="ZENODO_SANDBOX_TOKEN"
else
    TOKEN_VAR="ZENODO_PRODUCTION_TOKEN"
fi

if [[ -z "${!TOKEN_VAR:-}" && "$DRY_RUN" == false ]]; then
    echo "Warning: $TOKEN_VAR is not set. Set it if you intend to publish to Zenodo." >&2
fi


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------
if [[ "$DRY_RUN" == true ]]; then
    echo "=== DRY RUN — No files will be created or uploaded ==="
    echo ""
    echo "Configuration:"
    echo "  Parquet file:   $PARQUET_FILE"
    echo "  Version:        $VERSION"
    echo "  Title:          $TITLE"
    echo "  Description:    $DESCRIPTION"
    echo "  Creators:       $CREATORS"
    echo "  Environment:    $ENVIRONMENT"
    echo "  Output dir:     ${OUTPUT_DIR:-<temporary>}"
    echo ""
    echo "Validation passed. Run without --dry-run to create and publish."
    exit 0
fi


# ---------------------------------------------------------------------------
# Create and publish release
# ---------------------------------------------------------------------------
echo "Creating release archive for version $VERSION ..."

cd "$PROJECT_ROOT"

# Export the appropriate token so the Python ReleaseManager can find it
export "${TOKEN_VAR?}"

# Build the Python command
PYTHON_CMD="from nlp_policy_nz.integrations.release import ReleaseManager; import json; manager = ReleaseManager(); result = manager.full_release('$PARQUET_FILE', version='$VERSION', title='$TITLE', description='$DESCRIPTION', creators=json.loads('$CREATORS')); print(f'DOI: {result.get(\"doi\", \"N/A\")}')"

echo "Publishing to Zenodo ($ENVIRONMENT) ..."
CI=true python -c "$PYTHON_CMD"

echo ""
echo "✅ Release complete!"
echo "   Version: $VERSION"
echo "   Environment: $ENVIRONMENT"

