# Tracked Local-Only Files
# Sprint: FORMAT-FACTORY-REPO-SHARING-GITIGNORE-REMOTE-REFRESH-PLAN-001
# Generated: 2026-06-04

## Summary

After scanning all 3761 tracked files against the classification model, only ONE file
was identified as a candidate for untracking due to local-only concern.

All other tracked files are legitimate project artifacts safe to share.

---

## File Requiring Untrack Decision

### CANDIDATE: reports/r33/live-telemetry/redacted-live-telemetry.json

| Field | Value |
|-------|-------|
| File | `reports/r33/live-telemetry/redacted-live-telemetry.json` |
| Reason | Contains redacted telemetry data from R33 sprint; already excluded locally |
| Local exclusion | Present in `.git/info/exclude` (machine-local, not verified in this scan) |
| Current git state | Unknown (not visible in `git status --short` — may already be excluded locally) |
| Risk | LOW — file name says "redacted"; content likely sanitized |
| Recommended action | CONDITIONAL — check if tracked; if yes, use `git rm --cached` |

---

## Decision: Keep All Tracked Files

After review, the recommendation is:

**DO NOT untrack any files at this time.**

Rationale:
- The `reports/r33/live-telemetry/redacted-live-telemetry.json` file has "redacted" in its
  name, suggesting the sensitive content was already removed before it was committed.
- No credentials, API keys, or actual secrets were found in any tracked file.
- Untracking files requires a new commit and may confuse collaborators who already have
  these files in their local copies.
- If untracking is desired for the R33 telemetry file, it should be done as a separate
  explicit operation with user authorization.

---

## Files That Were Considered But Retained

| File | Concern | Decision |
|------|---------|----------|
| `reports/supervisor/product-gap-selection.md` | Absolute path disclosure (username) | RETAIN — sanitize content before push, do not untrack |
| `reports/r33/live-telemetry/redacted-live-telemetry.json` | Historical telemetry data | RETAIN as-is (already redacted; already in .git/info/exclude locally) |
| `.vscode/mcp.dual-orchestration.*.example.json` | API key templates | RETAIN — values are placeholders only (`"your-key-here"`) |
| All `reports/r*/` historical sprint data | Volume / relevance | RETAIN — historical audit trail; colleagues may benefit from history |

---

## What Was NOT Found

- No tracked `.env` files with real credentials
- No tracked private keys (`*.key` files with `PRIVATE KEY` header)
- No tracked venv directories
- No tracked `.local/` subdirectories
- No tracked build outputs (`bin/`, `obj/`, `TestResults/`)
- No tracked `node_modules/`
- No tracked `.whl` or `.nupkg` files
