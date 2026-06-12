# Durable Authority Extraction

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-AUTHORITY-HEALING-001
**Run ID:** master-plan-authority-healing-20260610
**Date:** 2026-06-11
**Source:** `docs/history/master-plan-full-before-healing-2026-06-10.md` (2229 lines)

## Classification of Removed Content

This document identifies which content from the original 2229-line plan was NOT preserved in the
408-line healed plan, and classifies each as: CRITICAL_MISSING (must restore) | ACCEPTABLE_LOSS
(archived with pointer, safe) | HISTORICAL_ONLY (safe to archive).

## CRITICAL_MISSING — Must Restore

### 1. Living Master Plan Policy (original §5, lines 100-110)

7 governing rules for how the master plan itself must be maintained. These are operational rules
that prevent the master plan from drifting again.

**Key rules not preserved:**
- Rule 2: "It is not a snapshot. It always reflects the current project state."
- Rule 4: "Generated summaries... must state: 'Generated summary — not authoritative.' They are never committed."
- Rule 5: "It must be reproducible from the repo state plus persisted local artifacts."
- Rule 6: "No section may be split out in a way that removes it from this document."
- Rule 7: "Agents must update this document after every gate transition."

**Current state:** These rules were not included in the healed plan. Only §18 Governance mentions sync policy via pointer.

**Action:** Add Section 5 (Living Master Plan Policy) with all 7 rules.

### 2. Persistent Artifact Model (original §15, lines 402-440)

Table of which artifacts are committed vs. local-only. Critical for preventing agents from
committing `.local/` files or treating generated summaries as authoritative.

**Key authority missing:**
- The full "Artifact Storage by Type" table (17 rows)
- The `.local/` directory structure and "gitignored, never committed" rule
- "`.local/` can be rebuilt from committed state if lost"

**Current state:** §12 (Evidence and Review Package) mentions `.local/evidences/` path but does
not contain the full artifact model.

**Action:** Add compact Persistent Artifact Model table to a new §22.

### 3. Reuse Decision Table (original §16, lines 442-462)

5-row decision table for when to reuse vs. regenerate artifacts. Operationally important.

**Current state:** §20 mentions "Reuse before regenerating" in a single line. No decision table.

**Action:** Add Reuse Decision Table to §22 alongside Persistent Artifact Model.

### 4. Format Expansion Guardrails (original §38.4, lines 1699-1720)

Key statement: "The system must not be limited to formats currently supported by Aspose."
Strategic direction for non-Aspose format backlog.

**Current state:** Not present in healed plan.

**Action:** Add compact §23 (Format Expansion Guardrails) with core principle.

### 5. Visibility Classification Table (original §17, lines 464-505)

6-class visibility schema with default classification rules per artifact type.

**Current state:** §18 mentions visibility classes as a brief list. No default classification table.

**Action:** Expand §18 with the default classification table (compact form).

## ACCEPTABLE_LOSS — Archived with Pointer, Safe

All of these exist in `docs/history/master-plan-archived-sections-2026-06-10.md` with ARCHIVE-PTR
pointers in the healed plan:

- Original §7 (Evidence Bundle Inspection Rule) — superseded by §12 declaration-driven model
- Original §9 (Phase 0 Required Files) — historical, 45-file list no longer operative
- Original §25 (Active Taskcards TC-0001..053) — historical execution state
- Original §27 (Gap Register) — historical gap tracking
- Original §28 (Healing Gap Register) — historical
- Original §31 (Phase 0 Review Checklist) — historical
- Original §32 (Run History Table) — historical execution logs
- Original §33 (Run Commit Ledger) — 380 lines of sprint history
- Original §36 (S-F2F Secondary Sprint) — HISTORICAL
- Original §37 (Format Understanding Layer) — UNAUTHORIZED_BACKLOG (noted in archive)
- Original §39 (AI/LLM Platform Layer) — UNAUTHORIZED_BACKLOG (noted in archive)

## HISTORICAL_ONLY — Safe to Leave in Archive

- Original §6 Current Project State table (500+ lines of sprint history)
- Original §8 Phase Model detailed narrative (summarized in current §14)
- Original §11 Codex secondary executor (DEC-014: deferred, not activated)
- Original §13 "No functional commands exist" (false, superseded by current commands)
- Original §24 WIP limits "1 format" (contradicted by poc-targets.yaml — corrected in §13)
- Original §29 Risk Register (condensed to risk summary sentence in §16)
- Original §30 Legacy ZIP bundle model (superseded by declaration-driven model)
- Original §40-43 (condensed into §§3-12 of healed plan)
