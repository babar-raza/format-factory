# Plan: Pilot-Identified Fix Sprint
# plan_id: pilot-fix-lle-2026-07-14
# type: machinery_hardening
# version: 1.0
# parent_plan: plans/.claude/lively-leaping-elephant.md (TERMINAL_CLOSED, hash=4ec7c2e738a598e3)
# created: 2026-07-14
# source_of_authority: pilot comparison run exposing 5 defects in lively-leaping-elephant deliverables

---

## Mission

Fix five defects discovered by the pilot end-to-end comparison run of the
lively-leaping-elephant governance sprint. All defects are in deliverables of the
parent plan. The parent plan is TERMINAL_CLOSED and must not be reopened.

## Non-Goals

- No product source changes
- No new validator additions
- No master plan structural changes
- No changes to the lively-leaping-elephant plan file itself

## Findings (from pilot)

| ID | Severity | Source | Description |
|----|----------|--------|-------------|
| FIND-001 | HIGH | TC-GOV-LLE-007 | `_compute_violation_pressure()` iterates `kv.values()` and calls `entry.get("path","")` — but baseline keys ARE the paths. All 337 entries silently skipped → `total=0` always |
| FIND-002 | MEDIUM | V139 | `governance_validators_found_issue.py:298` reads `declaration.get("tests_run", {})` as a dict; the field is `int` in schema — calls `.get()` on an int → V139-V142 all skip with `AttributeError` |
| FIND-003 | LOW | TC-GOV-LLE-010 | `reports/governance/validator-run-2026-07.txt` captured `FAIL=0` but actual run shows `FAIL=1` (V102); `blocks_sprint: False` stated but actual is `True` |
| FIND-004 | LOW | TC-GOV-LLE-010 | `reports/governance/validation-matrix-2026-07.md` §D claims "Entries past deadline: ~337" but actual count is 0 (all deadlines are 2026-09 or 2027-01, all future) |
| FIND-005 | LOW | runner | `ran(218) + skipped(4) = 222 ≠ expected(223)` with LLE declaration — one validator unaccounted for (likely a silent exception in a non-V139 try/except block) |

## Taskcard Register

### TC-PILOT-FIX-001: Fix violation_pressure key traversal
**Status: CLOSED** (fixed during pilot, staged in check_continuation.py)
**Proof target: 3 — integration test via _compute_violation_pressure() direct call**

Fix: changed `for entry in kv.values()` → `for path, entry in kv.items()` with `if not path.startswith("src/"): continue`
Result: `total=304, past_deadline=0, high_severity=11, level=HIGH` (correct)

Evidence: staged diff in tools/supervisor/check_continuation.py

### TC-PILOT-FIX-002: Fix V139 tests_run type coercion
**Status: CLOSED**
**Priority: HIGH**
**Proof target: 3 — V139-V142 no longer skipped with LLE declaration**

Root cause: `declaration.get("tests_run", {})` returns `int` (field holds total count),
then `.get("failed", 0)` throws `AttributeError: 'int' object has no attribute 'get'`.
The dict with pass/fail/skip is in `test_results`, not `tests_run`.

Fix: line 298 in `tools/supervisor/governance_validators_found_issue.py`:
```python
# BEFORE:
tests_run = declaration.get("tests_run", {}) or {}
failed_count = tests_run.get("failed", 0) or 0

# AFTER:
test_results = declaration.get("test_results", {}) or {}
if not isinstance(test_results, dict):
    test_results = {}
failed_count = test_results.get("failed", 0) or 0
```

Verification: run governance_validator_runner with LLE declaration → V139-V142 no longer in skipped list; ran+skipped delta improves

### TC-PILOT-FIX-003: Refresh validator-run-2026-07.txt
**Status: CLOSED**
**Priority: LOW**
**Proof target: 2 — file content matches actual run output**
**Dependency: TC-PILOT-FIX-002 (fix V139 first so count is correct)**

Recapture `reports/governance/validator-run-2026-07.txt` from an actual run of
`governance_validator_runner.py` with empty declaration.
Must accurately reflect: expected=223, ran=223 (after V139 fix), FAIL count, WARN count.

### TC-PILOT-FIX-004: Correct validation-matrix deadline claim
**Status: CLOSED**
**Priority: LOW**
**Proof target: 1 — file updated with correct claim**

In `reports/governance/validation-matrix-2026-07.md` §D, replace:
```
| Entries past deadline | ~337 (all deadline dates are pre-2026-07-14) |
```
With:
```
| Entries past deadline | 0 (all deadlines are 2026-09-01 or 2027-01-01 — future) |
| V193 will begin firing | 2026-09-01 (244 entries with 2026-09 deadline) |
```

Also update §B validation claim: "V193: WARN — many baseline entries have past
remediation_deadline" — correct to "V193: PASS — all deadline dates are future
(2026-09 or 2027-01); V193 will become active 2026-09-01"

### TC-PILOT-FIX-005: Investigate ran+skipped=222 delta
**Status: CLOSED — resolved by TC-PILOT-FIX-002**
**Priority: LOW**

With LLE declaration: ran(218) + skipped(4 V139-V142) = 222 ≠ expected(223), delta=-1.
With empty declaration: ran(223) + skipped(0) = 223. No delta.

Hypothesis: a second try/except block silently swallows one validator when
the LLE declaration triggers a code path that throws, but doesn't record it in
`skipped_validators`. This is a pre-existing runner bug.

Investigation: after TC-PILOT-FIX-002, rerun with LLE declaration and check if delta
resolves (V139 fix might unblock the accounting) or persists.

If delta persists after V139 fix: locate the silent swallower in the runner and fix.
If delta resolves: close as resolved by TC-PILOT-FIX-002.

## Dependency Order

```
TC-PILOT-FIX-001 (CLOSED — already fixed)
TC-PILOT-FIX-002 → TC-PILOT-FIX-003 → TC-PILOT-FIX-004
TC-PILOT-FIX-005 (investigate after TC-PILOT-FIX-002)
```

## Closeout Criteria

- TC-PILOT-FIX-001: CLOSED (staged)
- TC-PILOT-FIX-002: V139-V142 no longer in skipped list with real declarations
- TC-PILOT-FIX-003: validator-run-2026-07.txt reflects actual run metrics
- TC-PILOT-FIX-004: validation-matrix corrects deadline claim
- TC-PILOT-FIX-005: delta explained and fixed or confirmed resolved
- All tests still passing (no regressions)
- `ran + skipped = expected` for standard empty-declaration runs

## Evidence Requirements

- Raw `governance_validator_runner` output before/after V139 fix
- Direct invocation of V139 with LLE declaration before/after fix
- Updated file content for TC-003 and TC-004
- Test pass counts before and after

## Audit Gap Taskcards

(none yet — added after execution)


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-14T15:47:29.755231+00:00"
  locked_by: "f001e6ed7786"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
