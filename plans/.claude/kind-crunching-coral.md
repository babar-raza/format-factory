# Plan: GAP-DIF-FOSS-DIF_BOOLEAN_-001 — Production-Grade Gap Closure Design

## Problem Statement

The surface request is to close a single stale gap. The underlying problem is structural:
**8 gaps are in permanent limbo** — excluded from the work queue because they carry
`current_state: implementation_verified`, but never promoted to `status: closed` because
nothing in the pipeline performs that promotion. They cannot be selected as work items
(the compiler skips them) and cannot be auto-closed (the closure engine never sees them).
They will remain `open` indefinitely.

This plan repairs the specific case (3 DIF gaps + 5 install gaps) AND installs a durable
mechanism that prevents recurrence without weakening existing closure controls.

---

## Diagnosis: Symptoms vs. Root Causes vs. Structural Weaknesses

### Visible Symptoms
- `GAP-DIF-FOSS-DIF_BOOLEAN_-001` shows `status: open` despite 12 test calls and PROOF_LEVEL_4 verification
- 2 other DIF gaps (`DIF_DECLARED-001`, `DIF_SPECIAL_-001`) are in the same state
- 5 install gaps (FODS, FODT, PBM, PGM, PPM) are also in limbo
- `gap-closure-log.json` has exactly 1 entry after 7+ weeks of operation (0.07% closure rate)

### Root Cause (single, specific)

In `tools/supervisor/capability_feature_compiler.py:160-165` and
`tools/supervisor/capability_queue_consumer.py:51-58`, `implementation_verified`
is listed in `_SKIP_STATUSES` — meaning the pipeline correctly identifies these gaps
as "already implemented" and excludes them from work item generation. But the pipeline
stops there. No downstream step closes them.

The `gap_closure_engine.py` entry point `close_gaps_from_grades()` is called from
`autonomous_cycle.py:1183` and requires a `planned_work_item` with a `gap_ledger_ref`
pointing to the gap. But `implementation_verified` gaps are never selected as work
items (they're skipped), so they produce no `planned_work_item`, so the closure
engine's `_match_grades_to_gaps()` returns an empty list, so nothing closes.

**The invariant that is violated:** When the compiler trusts `implementation_verified`
enough to exclude a gap from work selection, it should also trust it enough to close it.
The two actions are in different parts of the pipeline with no handoff between them.

### Secondary Causes
- `gap_ledger_hygiene.py` exists for orphan detection but is not wired into any pipeline
- TC-C7-005 (autonomous_cycle.py:1147) merges `gap_ledger_ref` post-grading, which is
  too late — these gaps never reach grading at all
- `gap_type: missing_test_coverage` on these gaps is itself stale (tests were added in
  a later sprint but the field was never updated)
- No governance validator checks the `open + implementation_verified` combination

### Structural Weaknesses (distinct from root cause)
- **Gap lifecycle has no terminal event for the `implementation_verified` state**: There
  is a transition from `open → implementation_verified` (when source is found) but no
  defined transition from `implementation_verified → closed`. The state machine has a
  dead-end node.
- **Closure evidence is sprint-coupled**: The only path to closure runs through a sprint
  declaration and grading cycle. Pre-existing work that was never declared cannot close.
- **Dual ledger source** (`gap-ledger-active.json` vs `gap-ledger.json`) creates
  confusion at the closure step (autonomous_cycle.py:1188), though this is lower-priority.

---

## What to Preserve

The following mechanisms are working correctly and must not be changed:

- **`gap_closure_engine.py` `close_gaps_from_grades()`**: The declared-sprint closure
  path is correct. It requires evidence, grading, and test proof. This should remain the
  primary path for gaps that were actively targeted in a sprint.
- **TC-GUARD-001** (`guard_001_checker.py`): Enforces that declarations reference gaps.
  It should stay as-is — it guards a different problem (undeclared work).
- **`_SKIP_STATUSES` logic** in the compiler and queue consumer: Correctly excludes
  `implementation_verified` gaps from redundant work item generation. The fix must work
  alongside this, not replace it.
- **`gap-closure-log.json`** append-only audit trail: Keep as authoritative closure log.

---

## Solution Design

### Core Mechanism: `close_implementation_verified_gaps()` in `gap_closure_engine.py`

Add a second entry point to the existing closure engine (not a new file):

```python
def close_implementation_verified_gaps(
    gap_ledger_path: Path,
    test_root: Path,
    sprint_id: str,
    dry_run: bool = False,
) -> dict:
    """Close gaps whose current_state is implementation_verified, where test
    evidence is confirmed by scanning test files for function calls.

    This is the closure path for gaps that were excluded from work item selection
    (because they are already implemented) and thus never pass through the
    declared-sprint closure path. It does NOT replace that path.

    A gap is closed by this function only when ALL conditions hold:
    1. status == "open"
    2. current_state == "implementation_verified"
    3. The function name (derived from related_capability_id) appears in >= 1
       test file under test_root
    4. That test file actually imports the function or calls it (not just a comment)

    Gaps where no test file reference is found are promoted to
    current_state: "implementation_verified_no_tests" to surface them as
    genuinely needing test coverage.
    """
```

**Function name derivation logic:** `related_capability_id` follows the pattern
`DIF-FOSS-DIF_BOOLEAN_CELL_COUNT-SRC-001`. Extract the capability name segment,
lowercase and underscore-normalize it: `dif_boolean_cell_count`. Search test files
for this string.

**Closure metadata added to gap entry:**
```json
{
  "status": "closed",
  "closed_by_sprint": "<sprint_id>",
  "closed_at": "<iso_timestamp>",
  "closed_by_engine": true,
  "closure_method": "implementation_verified_test_scan",
  "closure_evidence": {
    "test_files_found": ["tests/python/dif/test_r1292_dif_gap_closure_cell_counts.py"],
    "call_count": 8,
    "scan_basis": "grep for function name in test files"
  }
}
```

**No-test-found path:** If scan finds no test file, update `current_state` from
`implementation_verified` to `implementation_verified_no_tests`. This makes the gap
eligible for work item selection again (remove `implementation_verified` from
`_SKIP_STATUSES` in both compiler and consumer, add
`implementation_verified_no_tests` there instead). The gap re-enters the work queue
as "needs test coverage."

### Integration: Wire into `autonomous_cycle.py`

Add a call immediately after TC-C7-005 (gap_ledger_ref merge, line 1147) and before
Step 3a-closure (line 1183):

```python
# Step 3a-pre2: Close implementation_verified gaps via test scan (TC-IMPL-CLOSE-001)
print("\n=== STEP 3a-pre2: IMPL-VERIFIED GAP CLOSURE SCAN ===")
try:
    _iv_result = close_implementation_verified_gaps(
        gap_ledger_path=_gl_path,
        test_root=repo_root / "tests",
        sprint_id=sprint_id,
    )
    print(f"  Closed {_iv_result['closed']} implementation_verified gaps via test scan")
    print(f"  Promoted {_iv_result.get('no_tests_found', 0)} to implementation_verified_no_tests")
except Exception as _iv_err:
    print(f"  WARNING: implementation_verified gap scan failed: {_iv_err}")
    # Best-effort — never blocks sprint continuation
```

### Immediate Fix for the 8 Limbo Gaps

The 8 currently-stuck gaps all have test evidence. They can be closed NOW by directly
updating the ledger (the scanner will confirm them, then mark closed). The scanner
handles this automatically when it first runs. No manual JSON editing needed — the
scanner IS the fix for current AND future cases.

### Governance Validator Addition

Add V-NEW (next available V-number, check `governance_validators_ext4.py`) to
`governance_validators_ext4.py`:

```
validate_no_open_implementation_verified_gaps():
    Scan gap-ledger.json for entries where status=open AND
    current_state=implementation_verified. If any exist, emit WARN (not BLOCK).
    Include gap_id list in the warning message.
    Rationale: These gaps are excluded from work queues AND not closed — they are
    invisible to both the work pipeline and the closure pipeline.
```

This validator makes the limbo state visible in governance output every sprint.

### `_SKIP_STATUSES` Correction

In both `capability_feature_compiler.py:162-167` and
`capability_queue_consumer.py:55-59`, replace `"implementation_verified"` with
`"implementation_verified_no_tests"` so that:
- Gaps with confirmed test coverage → scanner closes them → they leave the ledger
- Gaps with no test coverage → promoted to `implementation_verified_no_tests` → re-enter
  work queue for test writing → once tests are written and a sprint runs, declared-sprint
  closure path handles them

This makes the state machine complete: no dead-end nodes.

---

## Files to Modify

| File | Change |
|---|---|
| `tools/supervisor/gap_closure_engine.py` | Add `close_implementation_verified_gaps()` as second entry point (~80 lines) |
| `tools/supervisor/autonomous_cycle.py:~1147` | Wire in the new function call (Step 3a-pre2, ~15 lines) |
| `tools/supervisor/capability_feature_compiler.py:165` | Replace `"implementation_verified"` with `"implementation_verified_no_tests"` in `_SKIP_STATUSES` |
| `tools/supervisor/capability_queue_consumer.py:58` | Same replacement |
| `tools/supervisor/governance_validators_ext4.py` | Add V-NEW validator for open+implementation_verified |
| `tests/supervisor/test_gap_closure_engine.py` | Add tests for the new function (see Validation section) |

**Do NOT modify:**
- `reports/capability-layer/gap-ledger.json` manually — the scanner handles this
- `gap_closure_engine.py`'s existing `close_gaps_from_grades()` — leave untouched
- `guard_001_checker.py` — unrelated

---

## Validation Steps

### Unit Tests (add to `tests/supervisor/test_gap_closure_engine.py`)

1. **Happy path:** Build a temp gap ledger with 1 `open/implementation_verified` gap.
   Create a temp test file containing the function name. Assert gap is closed.

2. **No test file found:** Same setup but no test file. Assert gap is promoted to
   `implementation_verified_no_tests`, not closed.

3. **Already-closed gap:** Status already `closed`. Assert it is not re-processed.

4. **`gap_type` field updated:** When gap is closed by scanner, assert
   `closure_method == "implementation_verified_test_scan"`.

5. **Comment-only references don't count:** Test file contains `# dif_boolean_cell_count`
   but no actual call. Should not close. (Test the scan logic rigorously.)

6. **`_SKIP_STATUSES` regression test:** Assert `implementation_verified` is NOT in
   `_SKIP_STATUSES` after the fix. Assert `implementation_verified_no_tests` IS.
   This prevents silent reversion.

### Integration Test

After implementing, run:
```bash
# Dry-run of scanner against live ledger
python -c "
from pathlib import Path
from tools.supervisor.gap_closure_engine import close_implementation_verified_gaps
result = close_implementation_verified_gaps(
    Path('reports/capability-layer/gap-ledger.json'),
    Path('tests'),
    sprint_id='kind-crunching-coral',
    dry_run=True,
)
print(result)
"
```

Expected output: `closed: 8, no_tests_found: 0` for the current 8 limbo gaps.

Then re-run without `dry_run=True` to apply.

### Regression Control

Run after every change:
```bash
.venv/Scripts/pytest tests/supervisor/test_gap_closure_engine.py -v
.venv/Scripts/pytest tests/python/dif/ -q  # DIF suite should still pass
```

Governance validator run:
```bash
python tools/supervisor/governance_validator_runner.py
```
V-NEW should emit 0 warnings after the 8 gaps are closed.

---

## Tradeoffs and Risks

| Concern | Assessment |
|---|---|
| False positives (closing a gap where tests exist but fail) | The scanner only checks for test file presence, not test execution. Risk: a test file references the function but the test itself fails. **Mitigation:** In production, pair scanner with `pytest --collect-only` to verify the test is collectible. Long-term: integrate with test result cache. |
| `implementation_verified` set inaccurately by agent | The `current_state` field was written by prior agent sprints based on source introspection, not test execution. It could be wrong. **Mitigation:** The no-test-found path is a safety net: if the implementation doesn't actually exist, no test will reference it, so the gap gets promoted to `implementation_verified_no_tests` and re-enters the work queue. |
| `_SKIP_STATUSES` change re-enables `implementation_verified` gaps as work items | Only the ones without tests become re-eligible. If the current 8 all have tests (they do), they will be closed before the next compiler run, so they never re-enter the queue. |
| Dual ledger confusion (`gap-ledger-active.json`) | Out of scope for this plan. The scanner and the existing engine both use the same fallback logic — this plan doesn't worsen it. |
| `gap_ledger_hygiene.py` not wired in | Also out of scope — it handles orphaned/suspended capabilities, a separate concern. |
| V-NEW validator adding noise if limbo gaps accumulate again | This is intentional. The validator should emit WARN when limbo exists. If it's noisy, that means limbo is accumulating — which is exactly the signal we want. |

---

## What This Plan Does NOT Claim

- It does not guarantee 100% closure rate. Gaps with no test coverage will surface as
  `implementation_verified_no_tests` and need explicit sprint work.
- It does not fix the dual-ledger source issue. That requires a separate cleanup.
- It does not change the declared-sprint closure path. That path remains correct for
  actively-targeted gaps.
- It does not make `implementation_verified` an auto-close trigger without test
  confirmation. Test file presence is required.

---

## Taskcard Status Summary
(lifecycle_audit.py compatible)

| TC-ID | Status |
|-------|--------|
| TC-BOOL-001 | CLOSED |
| TC-BOOL-002 | CLOSED |
| TC-BOOL-003 | CLOSED |
| TC-BOOL-004 | CLOSED |
| TC-BOOL-005 | CLOSED |

---

## Taskcards

### TC-BOOL-001: Implement `close_implementation_verified_gaps()` | Status: CLOSED

Add to `tools/supervisor/gap_closure_engine.py`:
- Function signature with `gap_ledger_path`, `test_root`, `sprint_id`, `dry_run` params
- Capability name extraction from `related_capability_id`
- Test file scan (search for function name in `.py` files under `test_root`)
- Closure metadata: `closure_method: "implementation_verified_test_scan"`
- No-test-found promotion to `implementation_verified_no_tests`
- Append to `gap-closure-log.json` via existing `_append_closure_log()`
- Unit tests in `tests/supervisor/test_gap_closure_engine.py`

### TC-BOOL-002: Wire into `autonomous_cycle.py` | Status: CLOSED

Insert Step 3a-pre2 after line 1181 (TC-C7-005 block end), before line 1183 (Step 3a-closure).
Best-effort — catch all exceptions, never block continuation.

### TC-BOOL-003: Fix `_SKIP_STATUSES` in compiler and consumer | Status: CLOSED

In `capability_feature_compiler.py:165` and `capability_queue_consumer.py:58`:
Replace `"implementation_verified"` with `"implementation_verified_no_tests"`.
Add regression test asserting `implementation_verified` is NOT in `_SKIP_STATUSES`.

### TC-BOOL-004: Add V-NEW governance validator | Status: CLOSED

In `governance_validators_ext4.py`, add `validate_no_open_implementation_verified_gaps()`.
Check expected validator count in `governance_validator_runner.py` and update it.
Run governance suite to confirm no count regression.

### TC-BOOL-005: Run integration dry-run + apply + sprint closeout | Status: CLOSED

1. Run scanner dry-run, confirm 8 closures expected
2. Apply (live run) against gap-ledger.json
3. Verify gap-closure-log.json has 8 new entries
4. Run governance validator — V-NEW should show 0 warnings
5. Run `.venv/Scripts/pytest tests/python/dif/ -q` — all DIF tests pass
6. Run supervisor pipeline and commit


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-12T18:28:35.538021+00:00"
  locked_by: "93a9fa0ddc5b"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
