# parallel-foraging-fairy — Stub Enforcement Wiring + System Cleanup
# Plan Type: machinery_hardening
# Mission ID: PFF-FORENSICS-001
# Date: 2026-07-09 (third revision — verified against HEAD)
# Status: COMPLETE

---

## Context

The user asked "we have no stub policy, where is it defined and how well is it enforced."
Investigation revealed that `tools/review/no_stub_scan.py` exists and works but is
**never called by the governance pipeline**. V36 (stub tests) is WARN-only. V48
(architecture_only gate) only checks the `architecture_only` marker.

Two prior revisions of this plan contained errors. This revision verifies every item
against HEAD before including it.

---

## Taskcard Status Summary

| Taskcard | Status |
|---|---|
| TC-PFF-R1 | CLOSED |
| TC-PFF-R2 | CLOSED |
| TC-PFF-R3 | CLOSED |

---

## B. Item-by-Item Status of Previous Plan

### TC-PFF-R0 — Verify V87 DIF README freshness
**Status: OBSOLETE**
**Evidence:** V87 was demoted to `blocks_sprint: False` in ALL branches (commit `0c7ad33f`
"demote V87 readme freshness from FAIL to WARN"). It cannot block anything.
Lines 569, 577, 587 of `governance_validators_ext2.py` all show `blocks_sprint: False`.
The original premise (V87 blocking autonomous execution) is no longer true.

### TC-PFF-R1 — V149 validate_source_stubs
**Status: CLOSED**
**Evidence:** V149 implemented in `governance_validators_ext4.py`, registered in
`governance_validator_runner.py` (expected_count 166→167), tested in
`test_governance_validators.py` (2/2 PASS). WARN-only due to 9 pre-existing violations.
Delegates to `tools/review/no_stub_scan.py` report() function.

### TC-PFF-R2 — FODS nested duplicate cleanup
**Status: CLOSED**
**Evidence:** `src/python/fods/fods/` added to `.gitignore` under PIP EDITABLE-INSTALL
ARTIFACTS section. Canonical source confirmed at `src/python/fods/` (not the nested copy).

### TC-PFF-R3 — Stale test fixture reference
**Status: CLOSED**
**Evidence:** `test_lane_enforcement_validator.py` lines 68 and 99 changed from
`config_document.py` → `models.py`. All 11 tests PASS.

### TC-PFF-R4 — Pilot verification suite
**Status: OBSOLETE — scope reduced to V149 pilot only (covered by TC-PFF-R1)**

---

## C. Remaining Problems (verified, genuine)

### Problem 1: no_stub_scan.py not wired into governance pipeline
**Status: RESOLVED** — V149 `validate_source_stubs` created and registered.

### Problem 2: Stale test fixture reference
**Status: RESOLVED** — `config_document.py` → `models.py` at lines 68/99.

### Problem 3: Nested duplicate FODS package (`src/python/fods/fods/`)
**Status: RESOLVED** — Added to `.gitignore`.

---

## D. Revised Plan — Only Necessary Work

### Task 1: Create V149 `validate_source_stubs` (Priority: HIGH)
**Status: CLOSED**
- V149 added to `tools/supervisor/governance_validators_ext4.py`
- Registered in `tools/supervisor/governance_validator_runner.py` (expected_count=167)
- Tests: `TestV149ValidateSourceStubs` in `test_governance_validators.py` (2/2 PASS)
- WARN-only (`blocks_sprint: False`) due to 9 pre-existing violations

### Task 2: Fix stale test fixture reference (Priority: LOW)
**Status: CLOSED**
- `tests/supervisor/test_lane_enforcement_validator.py` lines 68, 99 fixed
- 11/11 tests PASS

### Task 3: Clean up nested FODS duplicate (Priority: LOW)
**Status: CLOSED**
- `src/python/fods/fods/` added to `.gitignore`

---

## What Was Removed From Previous Plan (and why)

| Removed Item | Reason |
|---|---|
| TC-PFF-R0 (V87 DIF verification) | V87 is `blocks_sprint: False` in ALL branches — cannot block anything |
| TC-PFF-R2 (FODS commit) | .NET Model + Python Compat already committed (b2d800fd, 55fd9453) |
| TC-PFF-R3 LOC regressions | Tracked in baseline; reduction is a separate sprint, not this plan's scope |
| TC-PFF-R3 streamed-jumping-oasis successor | Plan is TERMINAL_CLOSED; successor is a separate session |
| TC-PFF-R4 full pilot suite | Reduced to V149 pilot only — no systemic failures to diagnose |
| Plan lock conflict resolution | No production plan is IN_PROGRESS; active-plan-lock = TERMINAL_CLOSED |
| Continuation signal repair | Already repaired (global_repair_applied=true, iteration=0) |
| DIF analytics rename | V77 does NOT require dif_analytics.py; dif_stats.py is correct |
| bright-greeting-goose MOR | Separate plan, already TERMINAL_CLOSED across 3 sessions |

---

## Corrections to Previous Plan Errors

| Error | Reality |
|---|---|
| "V87 blocks_sprint=True" | V87 is `blocks_sprint: False` in ALL branches (demoted in 0c7ad33f) |
| "Validator count is 165" | Count is 166 (runner.py line 803) |
| "FODS files uncommitted" | Committed in b2d800fd + 55fd9453; remaining untracked files are nested duplicate |
| "active-plan-lock = bright-greeting-goose IN_PROGRESS" | Lock = jaunty-whistling-meteor TERMINAL_CLOSED |
| "22 IN_PROGRESS plan locks = production plans" | All 22 are pytest test artifacts in AppData/Local/Temp/ |
| "Test asserts exact validator count" | Test asserts `>= 154` (not exact); only runner expected_count needs update |


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-09T11:05:04.303695+00:00"
  locked_by: "f0490ee640cf"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
