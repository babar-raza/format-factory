# Review Execution Phases
# Format Factory — Expert Manual System Review
# Phase 8 output — Generated: 2026-06-25

## Overview

The expert review executes in 6 phases (A through F). Phase A is investigative (read-only).
Phases B-F move toward repair, but only after system gaps are healed first.

---

## Phase A — Investigation and Deep Analysis (read-only)

**Goal:** Confirm or refute each pre-identified problem. Produce verified problem matrix.

**Inputs:**
- All files in src/, tests/, registry/, poc-targets.yaml, reports/, .supervisor/

**Permitted actions:** Read-only. Writes go to reports/expert-manual-system-review/ only.

**Key investigations:**
1. Read FodsOdsExporter.cs fully — is it PROTOTYPE or functional?
2. Read all FODT test files — do they cover table structures?
3. Read ZST .NET fully — any decompression path?
4. Read gap-ledger.json first 20 entries — confirm "unknown" category pattern
5. Check skill registry for skills with empty implementation_paths
6. Check SAL cache: which formats have .json fact files

**Outputs:**
- `phase-a-investigation/confirmed-problems.json` — VERIFIED problem matrix (DONE this sprint)
- `phase-a-investigation/poc-targets-source-discrepancies.md` — PASS vs. source discrepancies
- `phase-a-investigation/test-quality-audit.md` — test classification by format
- `phase-a-investigation/system-gap-confirmed.md` — system gap confirmation

---

## Phase B — Problem Gathering and Confirmation

**Goal:** Finalize problem matrix with evidence-graded status for all items.

**Process:**
1. For each pre-identified problem, verify direct source evidence
2. Classify: system gap, product gap, or both
3. Identify which system component must be healed first
4. No source changes in this phase

**Priority classification:**
- System-blocking (PROB-009, PROB-010, PROB-011): fix before any product work
- Critical product gaps (PROB-001, PROB-002): fix after system healed
- High product gaps (PROB-003, PROB-006, PROB-013): fix in governed sprints
- Medium gaps (all others): deferred to scheduled sprints

**Outputs:**
- `phase-b-problems/verified-problem-matrix.json` — final verified matrix
- `phase-b-problems/system-gap-matrix.json` — system gaps only
- `phase-b-problems/product-gap-matrix.json` — product gaps only

---

## Phase C — Dry Run

**Goal:** Simulate review scoring. Verify methodology detects known issues.

**Methodology:**
1. Apply rubric to FODS .NET (expected: HIGH score ~3.7/5) ✓ Already done
2. Apply rubric to ZST .NET (expected: VERY LOW ~0.5/5) — gap between rich source context and empty product
3. Apply rubric to ODS Python (expected: MEDIUM ~2.5/5)
4. Verify rubric catches what is already known as gaps

**Pass criteria for dry run:**
- FODS scores above 3.5 (commercial candidate) ✓
- ZST scores below 2.0 (not a product)
- Known PROB items appear in rubric results as gaps

**Outputs:**
- `phase-c-dry-run/rubric-results.json` — scores per product
- `phase-c-dry-run/dry-run-methodology-proof.md` — confirms rubric works

---

## Phase D — Live Read-Only Run

**Goal:** Full review of every product using the rubric. Complete system layer review.

**Scope:**
1. Score all 10 .NET products (Tier 1/2/3)
2. Score all 20 Python products (PY-0 to PY-5 level)
3. Review all 7 system layers
4. Review evidence quality for last 5 sprint bundles

**Outputs:**
- `phase-d-live-run/dotnet-scored-matrix.json`
- `phase-d-live-run/python-scored-matrix.json`
- `phase-d-live-run/layer-scores.json`
- `phase-d-live-run/final-problem-matrix.json`
- `phase-d-live-run/solution-matrix.json`

---

## Phase E — Pilot Fix Plan

**Goal:** Choose one product + one system gap. Heal system first. Verify methodology.

**Recommended pilot targets (system gap first):**

**System pilot:** Gap ledger taxonomy repair (PROB-009)
- Root cause: gap_ledger_to_work_items.py does not populate category field
- Fix: Add category inference from gap content/capability type
- Verify: Rerun gap ledger generation → meaningful categories appear

**Product pilot:** ZST .NET decompression (PROB-001)
- Pre-condition: Gap ledger must track this with category "extraction_missing"
- Fix: Add ZstDecompressor.cs using System.IO.Compression or ZstdNet
- Verify: Test load.zst → decompress → verify content

**Pilot sequence:**
1. Fix gap category pipeline
2. Re-run gap ledger → confirm ZST decompression gap appears with real category
3. Use healed gap ledger to select ZST decompression fix
4. Implement fix through governed sprint
5. Verify gap ledger closes the entry

---

## Phase F — Unified Fix Execution

**Priority order for system-first healing:**

1. **Gap ledger taxonomy** (PROB-009) — FIRST. Enables everything else.
2. **SAL chain extension** (PROB-010) — Required for spec-parity grading of 10 formats
3. **Evidence quality fallback** (PROB-011) — Required for reliable grading
4. **poc-targets discrepancy fix** (PROB-013) — Authority layer repair
5. **ZST .NET decompression** (PROB-001) — Critical product gap (after PROB-009)
6. **PDF Unicode** (PROB-002) — High commercial gap
7. **FODT table model** (PROB-003) — Medium commercial gap
8. **FODP write_fodp** (PROB-006) — Medium FOSS gap
9. **CSV edit API** (PROB-005) — Medium commercial gap
10. **HTML/Markdown/TXT reclassification** (PROB-004) — Registry fix
11. **Analytics masquerade rename** (PROB-014) — Deferred governance debt
12. **Skills implementation_paths** (PROB-015) — Skills governance
