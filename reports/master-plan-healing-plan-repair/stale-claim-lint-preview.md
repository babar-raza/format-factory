# Stale-Claim Lint Preview — Master Plan Healing Plan Repair

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-GOVERNANCE-REVIEW-HEALING-PLAN-001
**Date:** 2026-06-10
**Source:** plans/master-plan.md (2229 lines)

## Scan Results

### Pattern 1: COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE
- **Line 9:** `COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001 (2026-05-13; FODS 42/42 PASS...`
  - Classification: **HISTORICAL_OK** — appears in run history context
- **Line 143:** `last_completed_sprint: ... COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001`
  - Classification: **STALE_CLAIM** — this is NOT the last completed sprint; hundreds of sprints have run since
- **Line 15:** `G11-D (edit-and-save vertical slice) DEMONSTRATED by COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001`
  - Classification: **STALE_CLAIM** — references this as the current state demonstration

### Pattern 2: No functional commands exist
- **Line 347:** `Phase 0 contains only .claude/commands/_readme.md. No functional commands exist yet.`
  - Classification: **FALSE_CLAIM** — 25 functional commands exist in .claude/commands/

### Pattern 3: bundle must be uploaded by human
- **Line 157:** `The latest evidence bundle must be uploaded by the human to an inspection environment.`
  - Classification: **STALE_CLAIM** — superseded by declaration-driven pipeline (Section 41)
- **Line 28:** `the latest evidence or source bundle must be uploaded, extracted, and inspected`
  - Classification: **STALE_CLAIM** — rule references legacy ZIP bundle model

### Pattern 4: Product stages WIP 1 format
- **Line 660:** `Product stages | Gates 10-11 | 1 format`
  - Classification: **FALSE_CLAIM** — 11 active POC targets exist (3 commercial + 8 FOSS)

### Pattern 5: Codex
- **Line 296:** `Codex (GitHub Copilot / OpenAI API) is an optional secondary executor.`
  - Classification: **STALE_CLAIM** — Codex has never been used, unsupported in current architecture
- **Line 377:** `Codex | OpenAI / GitHub Copilot — optional secondary`
  - Classification: **STALE_CLAIM** — same unsupported reference in LLM strategy table

### Pattern 6: SVG
- No references to "replace Netpbm with SVG" found in master plan.
  - Classification: **NOT_FOUND** — no SVG replacement pattern exists

### Pattern 7: commercial_product_ready.*true
- **0 matches found** — safety check PASS
  - Classification: **SAFE** — no false commercial readiness claims

### Pattern 8: not yet authorized
- **Line 1838-1843:** Section 39.8 "Implementation Not Yet Authorized"
  - Classification: **HISTORICAL_OK** — correctly labeled as unauthorized backlog
- **Line 1532:** S-F2F-05 through S-F2F-08: "proposed_pending_human_approval — NOT authorized"
  - Classification: **HISTORICAL_OK** — correctly labeled

### Pattern 9: Old run references in current-state claims
- **Line 143:** `last_completed_sprint: ... (2026-05-16; ZST Gate 3...)`
  - Classification: **STALE_CLAIM** — references R16/R15A era as "last completed"
- **Line 15:** `Gate 11 sub-gate G11-D ... by COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001`
  - Classification: **STALE_CLAIM** — references run048-era demonstration as current

### Pattern 10: Old sprint names in current-state
- **Line 9:** Multiple old sprint names referenced as current status
  - Classification: **STALE_CLAIM** — header "Current status" block is frozen at ~run048 era (2026-05-13)
- **Line 143:** `COMMERCIAL-LOAD-SAVE-VERTICAL-SLICE-SWARM-001` as last sprint
  - Classification: **STALE_CLAIM** — same frozen reference

## Summary

| Classification | Count |
|----------------|-------|
| FALSE_CLAIM | 2 |
| STALE_CLAIM | 10 |
| HISTORICAL_OK | 4 |
| SAFE | 1 |
| NOT_FOUND | 1 |

**Total findings:** 18 across 10 patterns.

All FALSE_CLAIM and STALE_CLAIM items must be resolved by the execution agent during the master plan healing sprint. HISTORICAL_OK items may remain if they are clearly labeled as historical context.
