# Phase Audit 4 Kickoff — FODS / FODT

**Sprint:** FORMAT-FACTORY-R50-EVIDENCE-CLOSEOUT-REPAIR-AND-OBJECT-MODEL-HARDENING-001
**Date:** 2026-05-22
**Phase:** 4 of 7 — Prototype Testing and Oracle Verification

---

## Phase 4 Description

Phase 4 covers the complete testing and oracle verification lifecycle for a format:
- Gate 5: Neutral model tests
- Gate 6: Oracle tests (verification of parsed output correctness)
- Gate 7: Fuzz and adversarial tests

FODS and FODT completed Gates 5-7 in prior sprints. This document kicks off Phase Audit 4
for these two formats by documenting the evidence state.

---

## Phase Audit 4 Criteria

| Criterion | Description |
|-----------|-------------|
| PA4-1 | Gate 5 neutral model tests exist and PASS |
| PA4-2 | Gate 6 oracle tests exist and PASS |
| PA4-3 | Gate 7 fuzz/adversarial tests exist and PASS |
| PA4-4 | Edge cases: empty files, max-size limits, encoding variants |
| PA4-5 | Read-write round-trip: parse → write → parse → verify (R49 POC) |
| PA4-6 | No undocumented behavior or overclaims in test suite |
| PA4-7 | commercial_product_ready: false in all test fixtures |
| PA4-8 | Test suite covers both Python FOSS and .NET tracks |
| PA4-9 | Preservation matrix documented (R49 deliverable) |

---

## FODS Phase Audit 4

### PA4-1: Gate 5 Neutral Model
- `tests/python/fods/test_fods_gate5_neutral_model.py`
- Status: **PASS** (R27)

### PA4-2: Gate 6 Oracle
- `tests/python/fods/test_fods_gate6_oracle_verification.py`
- Status: **PASS** (R27)

### PA4-3: Gate 7 Fuzz
- `tests/python/fods/test_fods_gate7_malformed_fuzz.py`
- Status: **PASS** (R27)

### PA4-4: Edge Cases
- Empty workbook, single cell, large workbook tests
- Status: **PARTIAL** — standard edge cases covered; max-size stress tests not yet added

### PA4-5: Round-Trip
- `tests/python/fods/test_r49_object_model_poc.py` (13 tests)
- `tests/python/fods/test_r50_fods_csv_export.py` (19 tests — export path)
- Status: **PASS** (R49 + R50)

### PA4-6: Overclaim Review
- `commercial_product_ready: false` in all sources
- Unsupported features documented (TC-FORMULA-001, TC-STYLE-001, TC-COLDEF-001)
- Status: **PASS**

### PA4-7: commercial_product_ready
- Status: **false** throughout

### PA4-8: Both Tracks
- Python FOSS: PASS (R49 POC)
- .NET commercial: PASS (R49 .NET POC; R50 .NET POC replay)
- Status: **PASS**

### PA4-9: Preservation Matrix
- `reports/r49/preservation-matrix-fods.md`
- Status: **DOCUMENTED**

**FODS Phase Audit 4 Result: PASS** (minor gap: max-size stress tests)

---

## FODT Phase Audit 4

### PA4-1: Gate 5 Neutral Model
- `tests/python/fodt/test_fodt_gate5_neutral_model.py`
- Status: **PASS** (R27)

### PA4-2: Gate 6 Oracle
- `tests/python/fodt/test_fodt_gate6_oracle_verification.py`
- Status: **PASS** (R27)

### PA4-3: Gate 7 Fuzz
- `tests/python/fodt/test_fodt_gate7_fuzz_guard.py`
- Status: **PASS** (R27)

### PA4-4: Edge Cases
- Empty document, headings-only, mixed blocks
- Status: **PARTIAL** — standard edge cases covered

### PA4-5: Round-Trip
- `tests/python/fodt/test_r49_object_model_poc.py` (12 tests)
- Includes R49 writer fix for blocks key + headings
- Status: **PASS** (R49)

### PA4-6: Overclaim Review
- Unsupported features documented (TC-INLINE-001, TC-TABLE-001, TC-LIST-001, TC-PARASTYLE-001)
- Status: **PASS**

### PA4-7: commercial_product_ready
- Status: **false** throughout

### PA4-8: Both Tracks
- Python FOSS: PASS (R49 POC)
- .NET commercial: PASS (R49 + R50 .NET POC)
- Status: **PASS**

### PA4-9: Preservation Matrix
- `reports/r49/preservation-matrix-fodt.md`
- Status: **DOCUMENTED**

**FODT Phase Audit 4 Result: PASS** (minor gap: max-size stress tests)

---

## Phase Audit 4 Summary

| Format | Result | Notes |
|--------|--------|-------|
| FODS | PASS | Minor gap: max-size stress tests |
| FODT | PASS | Minor gap: max-size stress tests |

`PHASE_AUDIT_4_KICKOFF: FODS_PASS_FODT_PASS`

---

## Phase Audit 4 — Other Formats

Phase Audit 4 for ZST/ODS/ODT requires PA3 completion first (PA3-1 and PA3-9 gaps pending).
Phase Audit 4 for those formats is deferred until PA3 gaps are closed.
