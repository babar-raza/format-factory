# Terminal Closure Hardening Delta

**Mission:** TC-FORENSICS-TERMINAL-20260623
**Generated:** 2026-06-23

## Summary of Code Changes

### TC-TCF-003: lifecycle_audit.py -- Plan File Taskcard Parser (D1, D2 fix)

**File:** `tools/supervisor/lifecycle_audit.py`

- Added `parse_plan_taskcards(plan_path)` function with 3 regex patterns (table, block, inline)
- Added `compute_plan_hash(plan_path)` returning SHA-256 of plan content
- Added `plan_path` parameter to `run_lifecycle_audit()` (backward-compatible, defaults to None)
- Added Section 5b: plan file taskcard check -- open taskcards generate CRITICAL findings
- Updated verdict logic: `has_open_taskcards` blocks `AUDIT_PASS`
- Added `build_closure_contract()` function returning dict with `closure_authorized` boolean
- Closure contract overrides verdict if `closure_authorized=False` but verdict was `AUDIT_PASS`
- Added `--plan-path` CLI argument
- Result dict now includes: `open_taskcards`, `all_taskcards_closed`, `total_taskcards_parsed`, `plan_path`, `plan_hash`, `closure_contract`

### TC-TCF-004: write_plan_lock.py -- Error Fallback + Audit Path (D4, D6 fix)

**File:** `tools/supervisor/write_plan_lock.py`

- Error fallback changed from `TERMINAL_CLOSED` to `ITERATION_REQUIRED` in both `except ImportError` and `except Exception` blocks
- Now passes `plan_path=plan_path` to `run_lifecycle_audit()` when `--audit-gate` is used
- Added warning when `--terminal` used without `--audit-gate`
- Added `--completion-candidate` CLI flag

### TC-TCF-005: COMPLETION_CANDIDATE State

**Files:** `write_plan_lock.py`, `check_continuation.py`, `autonomous_cycle.py`

- `COMPLETION_CANDIDATE` state added to `write_plan_lock.py` status selection logic
- `check_continuation.py` returns `CONTINUE` with `completion_candidate_detected: true` annotation
- `autonomous_cycle.py` Step 0b detects COMPLETION_CANDIDATE and prints advisory

### TC-TCF-006: Strict Closure Contract

**File:** `tools/supervisor/lifecycle_audit.py`

- `build_closure_contract()` returns dict with fields: `all_mandatory_tasks_closed`, `all_audit_findings_consumed`, `all_rework_closed`, `evidence_complete`, `no_govblock_unresolved`, `plan_hash`, `plan_path`, `closure_authorized`
- Contract included in `lifecycle-audit-results.json` output
- If `closure_authorized == False` AND `verdict == AUDIT_PASS`, verdict overridden to `AUDIT_REQUIRES_ITERATION`

### TC-TCF-007: reopen_plan_lock.py

**File:** `tools/supervisor/reopen_plan_lock.py` (NEW)

- CLI tool for governed reopening of TERMINAL_CLOSED plan locks
- `reopen_plan()`: transitions locks to IN_PROGRESS, preserves closure in `closure_history` array
- Appends to `.local/supervisor/reopening-register.json` with idempotency check
- Supports `--same-plan` (default) and `--successor` modes
- VALID_TRIGGERS enum for controlled reopening reasons

### TC-TCF-008: Autonomous Reopening Detection

**File:** `tools/supervisor/autonomous_cycle.py`

- Added Step 0b-reopen-check: scans TERMINAL_CLOSED locks for plans with open taskcards
- Calls `reopen_plan()` with trigger `AUTONOMOUS_OPEN_TASKCARD_DETECTION` if open TCs found
- Logs reopening events to `.local/supervisor/reopening-log.json`

### TC-TCF-009: Prevention Tests

**File:** `tests/supervisor/test_terminal_closure_prevention.py` (NEW -- 26 tests)

- TestParsePlanTaskcards: 7 tests
- TestComputePlanHash: 2 tests
- TestLifecycleAuditWithPlanPath: 4 tests
- TestClosureContract: 4 tests
- TestErrorFallbackSafety: 2 tests
- TestCompletionCandidate: 1 test
- TestReopenPlanLock: 4 tests
- TestNegativeControls: 2 tests

### TC-TCF-010: Governance Validators V60/V61

**File:** `tools/supervisor/governance_validators_ext.py`

- V60 `validate_terminal_closure_completeness`: WARN if RELEASE_GATE/READINESS items cite plans with open taskcards
- V61 `validate_error_fallback_safety`: FAIL if write_plan_lock.py error fallback assigns `status = "TERMINAL_CLOSED"` (D6 regression detection)

**File:** `tools/supervisor/governance_validator_runner.py`

- V60 and V61 registered in `run_all_governance_validators()`

## Defect Resolution Status

| Defect | Description | Fix | Status |
|--------|------------|-----|--------|
| D1 | lifecycle_audit.py never reads plan file | parse_plan_taskcards() + plan_path param | FIXED |
| D2 | No taskcard parser | 3-regex parser (table, block, inline) | FIXED |
| D3 | Rework findings ADVISORY only | CRITICAL severity findings block AUDIT_PASS | FIXED |
| D4 | --audit-gate optional | Warning added; plan_path passed to audit | FIXED |
| D5 | No plan file pre-check | Closure contract validates plan before lock | FIXED |
| D6 | Error fallback writes TERMINAL_CLOSED | Changed to ITERATION_REQUIRED | FIXED |
| D7 | No re-validation in check_continuation | COMPLETION_CANDIDATE state enables re-audit | PARTIALLY_FIXED |
| D8 | No stale audit check | Not addressed (low priority) | DEFERRED |
| D9 | No machine-readable taskcard format | Regex parser handles markdown patterns | FIXED |
| D10 | Inconsistent status markers | 3 regex patterns cover all observed patterns | FIXED |
| D11 | No premature closure tests | 26 tests in test_terminal_closure_prevention.py | FIXED |
| D12 | No reopening capability | reopen_plan_lock.py + autonomous detection | FIXED |
