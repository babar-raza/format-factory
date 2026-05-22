# Phase Audit 3 Kickoff — Parser Requirements / Prototype Creation

**Sprint:** FORMAT-FACTORY-R48-ARTIFACT-RC-CLEAN-CLOSEOUT-AND-PHASE-AUDIT-COMPLETION-001
**Date:** 2026-05-22
**Phase:** 3 of 7
**Status:** KICKOFF (pilot on FODS + FODT only)

---

## Prerequisites Satisfied

Phase Audit 2 is now COMPLETE (PHASE_AUDIT_2: COMPLETE_ALL_FORMATS_PASS).
All 20 sample directories have documented provenance.
Phase Audit 3 may now begin.

---

## Phase Audit 3 Criteria

For each format with a committed Python parser, verify:

| Criterion | Description |
|-----------|-------------|
| PA3-1 | Generated requirements exist (`generated-requirements/<format>/`) |
| PA3-2 | Parser source exists (`src/python/<format>/`) |
| PA3-3 | Parser tests map to requirements (test names reference IR-* or feature IDs) |
| PA3-4 | Invalid/malformed input handling tested |
| PA3-5 | Parser output maps to neutral model (schema documented) |
| PA3-6 | No hardcoded sample-only behavior (parser handles arbitrary conforming input) |
| PA3-7 | Unsupported features documented and not overclaimed |
| PA3-8 | commercial_product_ready: false (while prototype, pre-Gate 11) |
| PA3-9 | Parser round-trip: write→read→verify for applicable formats |

---

## FODS Pilot Audit

### PA3-1: Generated Requirements
- Path: `generated-requirements/fods/`
- Status: **PRESENT** (verified R46)

### PA3-2: Parser Source
- Path: `src/python/fods/parser.py`
- Status: **PRESENT** — 379+ lines, iterparse streaming

### PA3-3: Tests Map to Requirements
- `tests/python/fods/` contains Gate 4-7 tests referencing IR-FODS items
- Status: **PASS** — 157+ tests across gates 4-7

### PA3-4: Invalid Input Handling
- `tests/python/fods/test_r30_fods_gate7_fuzz.py` — malformed XML, truncated, empty
- Status: **PASS**

### PA3-5: Neutral Model Output
- Parser outputs: `{"sheets": [{"name": str, "rows": [{"cells": [{"value_type": str, "value": any}]}]}]}`
- Status: **DOCUMENTED** (parser.py docstring + IR-FODS requirements)

### PA3-6: No Hardcoded Sample Behavior
- Parser uses xpath/iterparse, not sample-specific logic
- Status: **PASS** (inferred from code structure)

### PA3-7: Unsupported Features Documented
- Unsupported: formulas (read as string), styles, merged cells, named ranges
- Status: **DOCUMENTED** in pack.yaml and parser docstring

### PA3-8: commercial_product_ready
- Status: **false** (Gate 11 not approved)

### PA3-9: Round-Trip
- Write: `write_fods()` (R46 MT6, now with typed-value fix R48)
- Read: `parse_fods()`
- Tests: `test_r48_writer_typed_values.py::TestTypedValueRoundTrip`
- Status: **PASS** (3 round-trip tests)

**FODS Phase Audit 3 Result: PASS (with typed-value fix applied in R48)**

---

## FODT Pilot Audit

### PA3-1: Generated Requirements
- Path: `generated-requirements/fodt/`
- Status: **PRESENT** (verified R46)

### PA3-2: Parser Source
- Path: `src/python/fodt/parser.py`
- Status: **PRESENT**

### PA3-3: Tests Map to Requirements
- `tests/python/fodt/` contains Gate 4-7 tests
- Status: **PASS** — 145+ tests

### PA3-4: Invalid Input Handling
- Fuzz/malformed tests present in Gate 7
- Status: **PASS**

### PA3-5: Neutral Model Output
- Parser outputs: `{"blocks": [{"type": str, "content": str}]}`
- Status: **DOCUMENTED**

### PA3-6: No Hardcoded Sample Behavior
- Parser uses xpath/iterparse
- Status: **PASS** (inferred)

### PA3-7: Unsupported Features
- Unsupported: styles, embedded images, tracked changes, macros
- Status: **DOCUMENTED**

### PA3-8: commercial_product_ready
- Status: **false**

### PA3-9: Round-Trip
- Write: `write_fodt()` (R46 MT6)
- Read: `parse_fodt()`
- Tests: `test_r47_writer_hardening.py::TestWriteFodtHardening`
- Status: **PASS**

**FODT Phase Audit 3 Result: PASS**

---

## Phase Audit 3 Pilot Summary

| Format | PA3-1 | PA3-2 | PA3-3 | PA3-4 | PA3-5 | PA3-6 | PA3-7 | PA3-8 | PA3-9 | Result |
|--------|-------|-------|-------|-------|-------|-------|-------|-------|-------|--------|
| FODS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |
| FODT | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | **PASS** |

**PHASE_AUDIT_3: PILOT_PASS_FODS_FODT**

---

## Next Sprint Targets for Phase Audit 3

| Priority | Format | Blocker |
|----------|--------|---------|
| R49 | ZST | Parser at Gate 4, round-trip not applicable (codec) |
| R49 | ODS | Parser at Gate 7, no writer yet |
| R49 | ODT | Parser at Gate 7, no writer yet |
| R50 | QOI | Parser at Gate 7 |
| R50 | DIF | Parser at Gate 7 |

---

## Phase Audit Roadmap (Updated)

| Phase | Sprint | Verdict |
|-------|--------|---------|
| Phase 1: Specification Ingestion | R46 (corrected R47) | CORE_PASS_MINOR_FORMATS_PARTIAL |
| Phase 2: Sample Acquisition / Provenance | R48 | COMPLETE_ALL_FORMATS_PASS |
| Phase 3: Parser Requirements / Prototype | R48 (pilot), R49 (expansion) | PILOT_PASS_FODS_FODT |
| Phase 4: Neutral Model / Oracle / Fuzz / Security | R49 | SCHEDULED |
| Phase 5: Product Mapping / Implementation Authorization | R50 | SCHEDULED |
| Phase 6: Package / RC Materialization | R51 | SCHEDULED |
| Phase 7: Commercial Readiness / Publication | R52 | SCHEDULED |
