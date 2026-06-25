# Evidence Quality Rubric
# Format Factory — Expert Manual System Review
# Phase 9 output — Generated: 2026-06-25

## Overview

Evidence bundles are the primary trust mechanism for the autonomous system.
This rubric defines what constitutes high-quality evidence.

---

## Evidence Quality Dimensions (0–5)

### EQ-1: Evidence Coverage

Proportion of sprint work items that have evidence.

| Score | Criteria |
|-------|---------|
| 0 | No evidence for any item |
| 1 | Evidence for <25% of items |
| 2 | Evidence for 25–50% of items |
| 3 | Evidence for 50–75% of items |
| 4 | Evidence for >75% of items |
| 5 | Evidence for all items; all paths verified |

---

### EQ-2: Evidence Specificity

Are evidence paths pointing to specific files (not directories)?

| Score | Criteria |
|-------|---------|
| 0 | No paths; just narrative |
| 1 | Directory paths only |
| 2 | File paths; no line references |
| 3 | File paths + function/class names |
| 4 | File paths + line references + code snippets |
| 5 | All of above + diff verification |

---

### EQ-3: Evidence Type Distribution

Mix of test files, source files, and output files.

| Score | Criteria |
|-------|---------|
| 0 | Narrative only |
| 1 | Source paths only; no tests |
| 2 | Source + test paths |
| 3 | Source + test + output (CSV, JSON, ZIP) |
| 4 | Source + test + output + physical file verification |
| 5 | All types + installed workflow proof |

---

### EQ-4: Grade Quality

Proportion of items graded vs. DEFERRED_WITH_REASON.

| Score | Criteria |
|-------|---------|
| 0 | All items DEFERRED (no LLM grader) |
| 1 | >50% DEFERRED |
| 2 | 25–50% DEFERRED |
| 3 | 10–25% DEFERRED |
| 4 | <10% DEFERRED |
| 5 | All items graded; no DEFERRED |

**Note:** DEFERRED occurs when LLM grader API keys are unavailable.

---

### EQ-5: Test Verification

Evidence references real test results (not synthetic).

| Score | Criteria |
|-------|---------|
| 0 | No test references |
| 1 | Test files listed but not run |
| 2 | Test count mentioned |
| 3 | Test names + pass/fail counts |
| 4 | Test names + test output excerpts |
| 5 | Full test run output with pass/fail per test |

---

### EQ-6: Physical Output Presence

Evidence includes physical output files (ZIP, PDF, PNG, CSV).

| Score | Criteria |
|-------|---------|
| 0 | No physical outputs referenced |
| 1 | Output filenames mentioned but not included |
| 2 | Output files exist in evidence bundle |
| 3 | Output files present + format verified (ZIP structure, valid CSV) |
| 4 | Output files verified in real application |
| 5 | Output files + automated verification script |

---

### EQ-7: Gap Closure Traceability

Each work item traces to a gap in the gap-ledger.

| Score | Criteria |
|-------|---------|
| 0 | No gap references |
| 1 | Some items have gap_ledger_ref |
| 2 | Most items have gap_ledger_ref |
| 3 | All items have gap_ledger_ref |
| 4 | All items with gap_ledger_ref + gap marked closed |
| 5 | Full chain: gap → work item → evidence → gap closed → validator prevents recurrence |

**Note:** gap_ledger_ref injection was added in 2026-06-24 to autonomous_cycle.py Step 3a-pre.

---

## Evidence Quality Scoring Bands

| Average (0–5) | Band |
|--------------|------|
| 0.0–1.4 | Inadequate — no trust basis |
| 1.5–2.4 | Minimal — advisory only |
| 2.5–3.4 | Adequate — supports sprint acceptance |
| 3.5–4.2 | Good — supports commercial gate review |
| 4.3–5.0 | Excellent — supports publication claim |

## Known Current State of Evidence System

| Dimension | Current State |
|-----------|--------------|
| EQ-4 Grade Quality | LOW — LLM grader often unavailable |
| EQ-6 Physical Outputs | LOW — not verified in CI |
| EQ-7 Gap Closure | MEDIUM — gap_ledger_ref injected (2026-06-24) but gap ledger taxonomy broken |

**Overall current evidence quality estimate:** 2.0–2.5 (Minimal to Adequate)

## Minimum Evidence Standards for Phase F Repairs

Before a product fix can be accepted as CLOSED:
- EQ-5 >= 3: Test names + pass/fail counts
- EQ-7 >= 3: Gap ledger entry traces to work item
- At least one physical output in evidence bundle (EQ-6 >= 2)
