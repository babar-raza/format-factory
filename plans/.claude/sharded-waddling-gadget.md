# Plan: Reconcile agile-rolling-marshmallow.md Stale Fields After TC-DL2-021 Closure

**Plan type:** plan_hardening
**Mission:** DUAL-LANE-PHASE2-001
**Target plan file:** `plans/.claude/agile-rolling-marshmallow.md`
**Created:** 2026-06-29

---

## Context

TC-DL2-021 (lane counter replay protection) was implemented and verified after the plan was hardened.
The implementation, tests, and plan's hardening sections all correctly reflect CLOSED status.
However, four stale field values remain in the plan that contradict the actual system state.
These stale fields create an inconsistency between the plan's executive summary data (accurate)
and its operational field values (stale). They must be corrected so the plan is self-consistent
and can pass any automated status check.

---

## A. Current-State Reassessment

**What changed since the previous plan cycle:**

| Change | Verified By |
|--------|-------------|
| `update_lane_counters` replay guard implemented (`last_applied_sprint_id` + ceiling check) | `autonomous_cycle_extensions/__init__.py` lines 208-243 |
| `test_duplicate_replay_double_increments` now asserts `== 1` (was `== 2`) | `test_lane_counter_replay.py` line 77 |
| 6 new TC-DL2-021 replay tests added | `test_lane_counter_replay.py` lines 79-137 |
| `test_replay_protection_prevents_double_increment` in regression suite asserts `== 1` | `test_dual_lane_regression.py` lines 132-142 |
| `test_command_file_exists` added to skills test; all 3 command files exist | `test_dual_lane_skills.py` lines 47-52; `.claude/commands/` verified |
| Plan hardening sections updated: TC-DL2-021 CLOSED, FIND-V01-003 RESOLVED | `plans/.claude/agile-rolling-marshmallow.md` lines 1418, 1511, 1528, 1603, 1607-1617 |

**Test count:** 76/76 PASS (was 68 before TC-DL2-021; plan incorrectly states 84/84).

---

## B. Item-by-Item Status of the Previous Plan

### TC-DL2-021: Lane Counter Replay Protection
**Status: SOLVED**

Evidence:
- `update_lane_counters` has `sprint_id` replay guard at line 228: `if sprint_id and entry.get("last_applied_sprint_id") == sprint_id: continue`
- `_dom_maturity_value` helper added; ceiling skip prevents lane_b from incrementing past ceiling
- `last_applied_sprint_id` written to ledger entry after each successful update (line 242)
- 10 tests in `test_lane_counter_replay.py` all PASS including `test_duplicate_replay_double_increments` (asserts `== 1`)
- Regression test renamed `test_replay_protection_prevents_double_increment` asserting `== 1`

### counter_replay_safety_proven: false
**Status: STALE — still false in the plan; should be true**

Evidence: `plans/.claude/agile-rolling-marshmallow.md` line 1307 reads:
`counter_replay_safety_proven: false  # DEFECT: ...`
But the defect is resolved. The comment and value are both stale.

### TC-DL2-019 status: CLOSED_WITH_KNOWN_DEFECT
**Status: STALE — TC-DL2-021 resolved the known defect; TC-DL2-019 should now be CLOSED**

Evidence: Line 1187 sets `**Status:** CLOSED_WITH_KNOWN_DEFECT`. The known defect note
at line 1190 says "Fix deferred to TC-DL2-021." TC-DL2-021 is now CLOSED. The deferral
has been executed. TC-DL2-019 should be promoted to CLOSED.

### Gate Contract at line 1549
**Status: STALE — "TC-DL2-019 must remain CLOSED_WITH_KNOWN_DEFECT until TC-DL2-021 passes"**

TC-DL2-021 has passed. The gate pre-condition is now obsolete; TC-DL2-019 should be CLOSED.

### Test count claim "84/84"
**Status: INACCURATE — actual count is 76/76**

Evidence: Live run output: `76 passed in 6.16s`. The plan says "84/84 dual-lane tests pass"
in lines 1522 and 1603. 76 is the correct count (19+17+8+4+6+10+12).

---

## C. Remaining Problems

All are metadata inconsistencies in `plans/.claude/agile-rolling-marshmallow.md`.
No code changes are required. All tests pass.

| # | Field | Current Value | Correct Value | Impact |
|---|-------|---------------|---------------|--------|
| 1 | `counter_replay_safety_proven` (line 1307) | `false` | `true` | Plan terminal gate reads this field; currently blocks clean re-closure |
| 2 | TC-DL2-019 `**Status:**` (line 1187) | `CLOSED_WITH_KNOWN_DEFECT` | `CLOSED` | Incorrect; defect is resolved |
| 3 | TC-DL2-019 known defect note (line 1190) | "Fix deferred to TC-DL2-021" | "Resolved by TC-DL2-021 (2026-06-29)" | Misleading after TC-DL2-021 closure |
| 4 | Test count claims (lines 1522, 1603) | "84/84" | "76/76" | Inaccurate count |

---

## D. Revised Plan (Only Necessary Work)

### Task 1: Fix counter_replay_safety_proven
**File:** `plans/.claude/agile-rolling-marshmallow.md` line 1307
**Change:** Replace:
```
  counter_replay_safety_proven: false  # DEFECT: duplicate replay double-increments (FIND-V01-003, TC-DL2-021)
```
with:
```
  counter_replay_safety_proven: true   # TC-DL2-021 CLOSED: replay guard in update_lane_counters (2026-06-29)
```

### Task 2: Promote TC-DL2-019 to CLOSED
**File:** `plans/.claude/agile-rolling-marshmallow.md` line 1187
**Change:** Replace:
```
**Type:** PARENT | **Status:** CLOSED_WITH_KNOWN_DEFECT
```
with:
```
**Type:** PARENT | **Status:** CLOSED
```

### Task 3: Update TC-DL2-019 known defect note
**File:** `plans/.claude/agile-rolling-marshmallow.md` line 1190
**Change:** Replace:
```
**Known Defect:** FIND-V01-003 — duplicate replay double-increments counters. Acceptance criterion "Replay safety proven (no double-update)" is NOT met. `test_duplicate_replay_double_increments` documents the defect. Fix deferred to TC-DL2-021.
```
with:
```
**Resolved Defect (2026-06-29):** FIND-V01-003 — duplicate replay double-increments was resolved by TC-DL2-021. `last_applied_sprint_id` guard added to `update_lane_counters`. `test_duplicate_replay_double_increments` now asserts `== 1` and passes. TC-DL2-019 acceptance criteria fully met.
```

### Task 4: Correct test count claims
**File:** `plans/.claude/agile-rolling-marshmallow.md`
**Change 4a** (line 1522): Replace `84/84 dual-lane tests pass (was 68)` with `76/76 dual-lane tests pass (was 68)`
**Change 4b** (line 1603): Replace `84/84 tests pass` with `76/76 tests pass`

### Task 5: Update Gate Contract (line 1549)
**File:** `plans/.claude/agile-rolling-marshmallow.md`
**Change:** Replace:
```
- **Pre-execution gate:** TC-DL2-019 must remain CLOSED_WITH_KNOWN_DEFECT until TC-DL2-021 passes. TC-DL2-021 does NOT block other plan work — it is an isolated fix with no downstream dependencies.
```
with:
```
- **Pre-execution gate:** TC-DL2-019 is CLOSED (defect resolved by TC-DL2-021, 2026-06-29). All taskcards are CLOSED. No execution gate is active.
```

### Task 6: Add hardening change log entry
**File:** `plans/.claude/agile-rolling-marshmallow.md`
**Change:** Append row to change log table after line 1505:
```
| 2026-06-29 | Corrected stale fields: counter_replay_safety_proven→true, TC-DL2-019→CLOSED, test count 84→76 | State reassessment against 76/76 test run |
```

---

## Verification

After applying all 6 tasks, verify:

```bash
# 1. counter_replay_safety_proven is now true
grep "counter_replay_safety_proven" plans/.claude/agile-rolling-marshmallow.md

# 2. TC-DL2-019 is CLOSED (not CLOSED_WITH_KNOWN_DEFECT)
grep "TC-DL2-019" plans/.claude/agile-rolling-marshmallow.md | grep "Status"

# 3. No "84/84" remains
grep "84/84" plans/.claude/agile-rolling-marshmallow.md  # should return nothing

# 4. Status count: all CLOSED
python -c "
import re
text = open('plans/.claude/agile-rolling-marshmallow.md', encoding='utf-8').read()
from collections import Counter
c = Counter(m.group(1) for m in re.finditer(r'\*\*Status:\*\*\s+(\S+)', text))
print(c)
# Expected: {'CLOSED': 57} — 56 existing + TC-DL2-019 upgraded from CLOSED_WITH_KNOWN_DEFECT
"

# 5. Tests still pass
.venv/Scripts/python -m pytest tests/supervisor/test_lane_counter_replay.py tests/supervisor/test_dual_lane_skills.py tests/supervisor/test_dual_lane_regression.py -v --tb=short
```

Expected results:
- `counter_replay_safety_proven: true`
- TC-DL2-019 status: CLOSED
- No "84/84" occurrences
- Status counter: `{'CLOSED': 57}` (all taskcards CLOSED including TC-DL2-019)
- 76/76 tests PASS

---

## Scope Boundaries

**In scope:** Metadata field corrections in `plans/.claude/agile-rolling-marshmallow.md` only.

**Out of scope:** No code changes. No new tests. No governance file changes. No plan lock changes (terminal lock is already TERMINAL_CLOSED at line 1608). No CI changes.

---

## Taskcard Summary

| ID | Action | File | Lines | Complexity |
|----|--------|------|-------|------------|
| P1 | Fix counter_replay_safety_proven | agile-rolling-marshmallow.md | 1307 | 1 line |
| P2 | Promote TC-DL2-019 to CLOSED | agile-rolling-marshmallow.md | 1187 | 1 line |
| P3 | Update TC-DL2-019 defect note | agile-rolling-marshmallow.md | 1190 | 1 line |
| P4a | Fix test count (Resolved Work) | agile-rolling-marshmallow.md | 1522 | 1 line |
| P4b | Fix test count (Remaining Blockers) | agile-rolling-marshmallow.md | 1603 | 1 line |
| P5 | Update Gate Contract | agile-rolling-marshmallow.md | 1549-1551 | 1 line |
| P6 | Add change log entry | agile-rolling-marshmallow.md | after 1505 | 1 line |

All 7 changes are single-line edits. No risk of introducing regressions.
No code, no tests, no infrastructure — metadata reconciliation only.


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-02T09:25:49.818627+00:00"
  locked_by: "e832837e0867"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
