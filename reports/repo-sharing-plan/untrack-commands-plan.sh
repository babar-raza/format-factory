#!/bin/bash
# Untrack Commands Plan
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04
#
# IMPORTANT: This is a PLAN file. These commands are NOT executed automatically.
# Review this file and execute the commands manually only after user authorization.
#
# Current recommendation: NO files need to be untracked at this time.
# See tracked-local-only-files.md for full analysis.
#
# ---------------------------------------------------------------------------
# CONDITIONAL: R33 live telemetry (only if file is tracked and user authorizes)
# ---------------------------------------------------------------------------
#
# To check if this file is currently tracked:
#   git ls-files --error-unmatch reports/r33/live-telemetry/redacted-live-telemetry.json
#   # Exit 0 = tracked; Exit 1 = not tracked
#
# To untrack WITHOUT deleting the local file (if authorized):
#   git rm --cached reports/r33/live-telemetry/redacted-live-telemetry.json
#
# After untracking, add to .gitignore:
#   echo "reports/r33/live-telemetry/" >> .gitignore
#
# Then commit:
#   git commit -m "chore: untrack R33 live telemetry file (local-only data)"
#
# ---------------------------------------------------------------------------
# SANITIZE (required before push — NOT an untrack operation):
# ---------------------------------------------------------------------------
#
# Sanitize absolute path in product-gap-selection.md:
#   sed -i 's|C:/Users/prora/OneDrive/Documents/GitHub/format-factory/|./|g' \
#     reports/supervisor/product-gap-selection.md
#
# Verify sanitization:
#   head -3 reports/supervisor/product-gap-selection.md | grep -i "prora"
#   # Must return empty
#
# ---------------------------------------------------------------------------
# END OF PLAN — NO COMMANDS ARE EXECUTED BY THIS SCRIPT
# ---------------------------------------------------------------------------
echo "This is a plan file. Read the comments above before executing any commands."
exit 0
