#!/usr/bin/env bash
# autonomous_external_host.sh
# Format Factory External Autonomous Host Loop Bootstrap (Bash/Git Bash/WSL)
#
# Run this script from a terminal OUTSIDE of VS Code / Claude Code.
# It removes CLAUDECODE from the environment and starts the host loop.
#
# Usage:
#   cd /c/Users/prora/OneDrive/Documents/GitHub/format-factory
#   bash scripts/autonomous_external_host.sh
#
# For dry-run:
#   bash scripts/autonomous_external_host.sh --dry-run

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
echo "Repo root: $REPO_ROOT"

# Remove CLAUDECODE from environment
if [ -n "${CLAUDECODE:-}" ]; then
    echo "Removing CLAUDECODE from environment (was: $CLAUDECODE)"
    unset CLAUDECODE
else
    echo "CLAUDECODE not set (good — not running inside Claude Code)"
fi

# Detect Python
PYTHON=".local/venv/Scripts/python"
if [ ! -f "$PYTHON" ]; then
    PYTHON=".local/venv/bin/python"
fi
if [ ! -f "$PYTHON" ]; then
    PYTHON="python"
fi
echo "Python: $PYTHON"
$PYTHON --version

# Default args
NEXT_ACTION="reports/autonomous-external-host-bootstrap/next-action.json"
OUTPUT_DIR="reports/autonomous-external-host-bootstrap/host-loop"
DRY_RUN_FLAG=""

for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN_FLAG="--dry-run" ;;
        --next-action=*) NEXT_ACTION="${arg#*=}" ;;
        --output-dir=*) OUTPUT_DIR="${arg#*=}" ;;
    esac
done

if [ -n "$DRY_RUN_FLAG" ]; then
    echo "MODE: DRY RUN"
else
    echo "MODE: LIVE (will invoke Claude CLI)"
fi

echo ""
echo "Starting external host loop..."
$PYTHON tools/supervisor/external_host_loop.py \
    --next-action "$NEXT_ACTION" \
    --output-dir "$OUTPUT_DIR" \
    --repo-root "$REPO_ROOT" \
    $DRY_RUN_FLAG

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "HOST LOOP: SUCCESS (exit 0)"
else
    echo "HOST LOOP: FAILED or BLOCKED (exit $EXIT_CODE)"
fi

RESULT_PATH="$OUTPUT_DIR/host-loop-result.json"
if [ -f "$RESULT_PATH" ]; then
    echo "Result: $RESULT_PATH"
    cat "$RESULT_PATH"
fi

exit $EXIT_CODE
