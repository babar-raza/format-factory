# Package Gap Analysis
# Sprint: FORMAT-FACTORY-LOCAL-MEMORY-SYNC-EVIDENCE-PACKAGE-REPAIR-001
# Date: 2026-06-04

## Original Package

- **Path:** `.local/supervisor/reviews/local-memory-sync/declaration-review-package.zip`
- **SHA-256:** `ca54b1e9a6db002f66ee1960130b53aa600f3772013f52287c8878787b0570b1`
- **Entries:** 24

## Gap Analysis

### What the Original ZIP Contains
The original package was built by `build_declaration_review_package.py` using the standard supervisor template. It contains:

```
evidence/evidence-declaration.yaml       ← included (correct)
evidence/evidence-manifest.yaml          ← included (correct)
global-state/context-pack.yaml           ← STALE (Mainstream R113)
global-state/continuation-signal.json   ← STALE (Mainstream R113)
global-state/mcp.json                    ← STALE (not relevant to memory sync)
global-state/poc-targets.yaml            ← STALE (Mainstream R113)
global-state/product-code-change-ledger.json ← STALE
global-state/selected-product-gaps.json ← STALE
global-state/supervisor/approval-gates.md ← STALE (Mainstream R113)
global-state/supervisor/context-pack.md  ← STALE
global-state/supervisor/contradictions.md ← STALE
global-state/supervisor/evidence-review.md ← STALE
global-state/supervisor/latest-cycle-summary.md ← STALE (Mainstream R113)
global-state/supervisor/mcp-status.json  ← STALE
global-state/supervisor/mcp-status.md   ← STALE
global-state/supervisor/next-sprint.md  ← STALE (Mainstream R113)
global-state/supervisor/session-resume.md ← STALE
historical/r91-work-item-grades.json     ← STALE (old sprint)
historical/r91-work-item-grades.md       ← STALE (old sprint)
package-manifest.json                    ← included (but generic)
supervisor/materialized-evidence-review.md ← STALE
supervisor/work-item-grades.json         ← STALE
supervisor/work-item-grades.md           ← STALE
supervisor/work-item-grades.yaml         ← STALE
```

### What the Original ZIP Is Missing (ALL of these)

**Sprint Reports (16 files):**
- reports/local-memory-sync/preflight.md
- reports/local-memory-sync/read-files.md
- reports/local-memory-sync/allowed-paths.md
- reports/local-memory-sync/forbidden-paths.md
- reports/local-memory-sync/taskcard-state.json
- reports/local-memory-sync/product-first-sync.md
- reports/local-memory-sync/four-stream-sync.md
- reports/local-memory-sync/ai-operating-model-sync.md
- reports/local-memory-sync/external-tool-sync.md
- reports/local-memory-sync/mainstream-train-sync.md
- reports/local-memory-sync/plan-status-sync.md
- reports/local-memory-sync/prompt-template-sync.md
- reports/local-memory-sync/validation-results.md
- reports/local-memory-sync/changed-files.md
- reports/local-memory-sync/final-git-status.txt
- reports/local-memory-sync/review-package-proof.md

**Governance Docs (8 files):**
- docs/governance/four-stream-operating-model.md
- docs/governance/ai-authority-boundary.md
- docs/governance/external-tool-architecture.md
- docs/governance/ruflo-runtime-governance.md
- docs/governance/superpowers-skill-intake.md
- docs/governance/ghidra-mcp-compliance-gate.md
- docs/governance/mainstream-poc-mega-train.md
- docs/governance/product-first-operating-model.md (updated)

**Prompt Templates (4 files):**
- docs/prompt-templates/mainstream-poc-mega-train-template.md
- docs/prompt-templates/format-factory-stream-prompt-requirements.md
- docs/prompt-templates/external-tool-aware-repair-template.md
- docs/prompt-templates/repair-order-reference.md

**State (1 file):**
- state/current-state.md

**Total missing from original ZIP: 29 files**

## Root Cause

The standard `build_declaration_review_package.py` tool uses a generic supervisor bundle template that:
1. Pulls global-state from the repo's active supervisor output directories
2. Does NOT traverse the specific declared evidence paths from the declaration YAML
3. Includes historical sprint grades that are unrelated to this sprint
4. Excludes the actual sprint deliverables (docs, templates, reports)

## Repair Plan

Build a new self-contained ZIP that:
1. Includes all 31 declared files from evidence-manifest.yaml
2. Excludes stale global-state from Mainstream R113 (or marks as historical_context_only)
3. Includes the repair reports from this sprint
4. Is independently reviewable without access to the repo
