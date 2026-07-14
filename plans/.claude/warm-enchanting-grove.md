# Plan: LLM Grader — Production Reliability Hardening
# AUTHORITATIVE EXECUTION PLAN — warm-enchanting-grove
# plan_path: plans/.claude/warm-enchanting-grove.md
# authority: SINGLE_AUTHORITATIVE_PLAN
# version: 2 (micro-taskcardized)
# execution_authority: true

---

## [SECTION A] PREFLIGHT RECORDS

```yaml
# artifact_role: preflight_record
# execution_authority: false
# authoritative_plan: C:\Users\prora\.claude\plans\warm-enchanting-grove.md

taskcardization-preflight:
  repository_path: c:\Users\prora\OneDrive\Documents\GitHub\format-factory
  branch: main
  active_plan_path: C:\Users\prora\.claude\plans\warm-enchanting-grove.md
  active_plan_title: "LLM Grader — Production Reliability Hardening"
  plan_format: markdown
  authority_source: explicit_plan_mode_attachment
  approximate_plan_size_v1: 540 lines
  major_section_count: 9
  existing_taskcard_sections: 7 (TC-LGT-001 through TC-LGT-007, prose-only, no hierarchy)
  existing_taskcard_format: prose description only, no machine state
  existing_lanes: none
  existing_waves: none
  existing_gates: none listed
  existing_state_vocabulary: none
  existing_validation_model: 6 verification steps (prose)
  existing_evidence_model: none structured
  existing_normalization_conventions: TC-LGT-NNN
  existing_naming_conventions: REL-NNN for tests, MS- not yet used
  existing_execution_handoff: none
  duplicate_plan_risk: LOW — only one plan file found

active-plan-authority-verdict:
  verdict: SINGLE_PLAN_CONFIRMED
  authoritative_path: C:\Users\prora\.claude\plans\warm-enchanting-grove.md
  competing_plans: none found
  stale_plans: v1 contents superseded by this v2 (in-place update, not a new file)

duplicate-plan-risk-check:
  risk_level: LOW
  note: Only one plan file exists. The v2 update is in-place. No competing plan created.
```

---

## [SECTION B] PLAN ANALYSIS — PRESERVED FINDINGS

### B.1 Context

A network timeout was reported during an LLM grader call to OpenAI ("SSL read or network
read timeout"). Investigation of the grader event log and source code reveals several
overlapping problems. The most important finding is that **the event log contains ~72%
test artifacts**, which makes the incident look more severe than it is and makes diagnosis
nearly impossible. The actual production failures are real but much narrower.

This plan separates what is already correct from what needs to change, explains why
grading is inconsistent across reruns, and proposes concrete changes in priority order
with clear tradeoffs.

### B.2 What is already correct (do not disturb)

- `grader_reliability.py` — 16-class error taxonomy, exponential backoff with jitter,
  deadline awareness, Retry-After support, structured GradingObserver. This is solid.
- `call_with_retry()` — correct implementation; tested REL-001 to REL-020.
- `_sv_sdk_fallback()` in `grade_declared_work.py` — uses `call_with_retry` with
  `RetryPolicy(max_attempts=3, read=30s, overall_deadline=95s)` and httpx.Timeout correctly.
- Grade cache — 7-day TTL, content-addressed via SHA-256 of evidence file bytes.
- Level 2 fallback — `grade_intermediate_verify` is tried and cached (`iv:` prefix)
  when LLM fails (`grade_declared_work.py:480-485`).
- temperature=0 everywhere — correct for determinism within a provider.
- Evidence hash (`_evidence_hash`) — stable given identical inputs; covers file content
  fingerprints so any evidence change invalidates cache correctly.
- Existing tests REL-001 to REL-020 — all valid; must remain passing after changes.

### B.3 Root Causes (evidence-backed, confidence-graded)

**RC-1 (HIGH confidence): Tests write to the production event log**

`grader-events.jsonl` analysis:
- 777 of 863 events have `duration_ms=0` or `duration_ms=50000`
- The `50000ms` events originate from `TestCallWithRetryDeadline.test_deadline_aborts_retries`
  in `tests/supervisor/test_grader_reliability.py` which patches `time.monotonic` to
  increment by 50s per tick — `duration_ms = int(50.0 × 1000) = 50000` exactly.
- REL-012 (`ITEM-T`), REL-013 (empty item_id, READ_TIMEOUT), REL-015 (50000ms) all use
  the default `GradingObserver()` which writes to `.local/llm-call-logs/grader-events.jsonl`
  — the real production log.
- The "SSL read timeout" incident that triggered this work is likely a test artifact.
- Real production failures exist but are buried in test noise. Impossible to diagnose.

**RC-2 (HIGH confidence): Gateway call path has no retry or observability**

`grade_declared_work.py:236-256`, `_sv_llm_call`:
```python
try:
    resp, _record = gw(config=cfg, model="recommended", messages=messages, ...)
    content = resp.get("content", "")
    ...
except Exception as exc:
    print(f"  [LLM] gateway_chat exception ...")
    return None   # ← no retry, no grading event, silent failure
```
Gateway is the PRIMARY code path (called before SDK fallback). No retry, no backoff,
zero grading events on failure. Silent grade degradation when gateway has transient errors.

Also broken: `adversarial_check.py:63-70` — same bare-except pattern.

**RC-3 (HIGH confidence): No circuit breaker**

No circuit state exists in `grader_reliability.py` or `grade_declared_work.py`.
Each item independently retries 3×.

Worst-case: 15 items × 3 attempts × (30s read + 8s backoff) = 19 minutes blocked
during a complete provider outage.

**RC-4 (MEDIUM confidence): LLM failure not consistently cached — rerun inconsistency**

Cache write locations in `semantic_verify_item` (`grade_declared_work.py:362-489`):
```
LLM succeeds → parsed → _cache_grade() at line 470                    [CACHED 7d]
LLM fails → grade_intermediate_verify → _cache_grade("iv:") line 483  [CACHED 7d]
LLM fails + intermediate unavailable → hardcoded fallback lines 487-9  [NOT CACHED]
```
Terminal fallback is NOT cached. Grade flips between runs depending on LLM availability.

**RC-5 (MEDIUM confidence): Gateway/SDK fallback detection is fragile**

`grade_declared_work.py:248-252`:
```python
if _record and getattr(_record, "status", None) and "error" in str(_record.status).lower():
    return _sv_sdk_fallback(messages, cfg, item_id=item_id)
```
SDK fallback fires only when: exception NOT raised AND `_record` exists AND `_record.status`
contains "error". When gateway raises exception, `_record` is never set → SDK fallback
is NEVER called → None returned when SDK would have succeeded.

### B.4 Out of Scope (accepted limitations)

- **LLM non-determinism across model versions**: temperature=0 without seed. Fixing
  requires a golden test set and grading calibration. Out of scope.
- **False positive hallucination**: No guard against confident "adequate:true" hallucination.
  Requires multi-judge consensus. Out of scope.
- **Distributed circuit breaker**: Process-level only. Single-process use case is sufficient.
  Redis/file-backed implementation deferred.

### B.5 Tradeoffs (must be understood before executing)

- **Circuit breaker opens after 5 consecutive failures**: 6th item in a burst gets
  `CIRCUIT_OPEN` immediately. Force-close requires process restart. 60s cooldown then
  probes. This is correct behavior for a down provider.
- **30-min failure TTL creates write spike after recovery**: When TTL expires for all items
  simultaneously, next run calls LLM for all items at once. Mitigation: add per-item
  random jitter (0-5 min) to failure TTL.
- **Gateway retry (max 45s total) delays SDK fallback**: If gateway is misconfigured,
  2 retries add ~6s before falling through to SDK. Mitigation: probe once at
  `_get_sv_gateway()` init; skip gateway on permanent failure.
- **Observer isolation may surface hidden test failures**: Tests relying on default observer
  swallowing write errors will become visible. This is correct behavior.

### B.6 Confidence Assessment

| Finding | Confidence | Basis |
|---|---|---|
| Test artifacts dominate log | HIGH | 50000ms = fake_monotonic(50s); item_id="" matches REL-01x |
| Gateway path has no retry | HIGH | Direct code inspection grade_declared_work.py:236-256 |
| No circuit breaker | HIGH | Direct code inspection grader_reliability.py full read |
| Failure cache gap → rerun inconsistency | MEDIUM | Manifests only when grade_intermediate_verify unavailable |
| Gateway/SDK fallback detection fragile | MEDIUM | _record.status substring requires gateway to NOT raise |
| Actual production SSL timeout severity | LOW | Log contaminated; isolatable only after RC-1 fix |

---

## [SECTION C] REQUIREMENTS INVENTORY

```yaml
# artifact_role: normalized_requirements_inventory
# execution_authority: false
# authoritative_plan: warm-enchanting-grove.md

requirements:
  REQ-LGT-001:
    title: Env-variable override for grader log directory
    source_section: B.3 RC-1
    rationale: Enables tests to route GradingObserver writes to tmp_path without touching production log
    affected_files: [tools/supervisor/grader_reliability.py]
    acceptance: GRADER_LOG_DIR env var respected; default behavior unchanged when unset

  REQ-LGT-002:
    title: Fix all existing tests to use isolated observers
    source_section: B.3 RC-1
    rationale: Stops test artifacts from contaminating production grader-events.jsonl
    affected_files: [tests/supervisor/test_grader_reliability.py]
    acceptance: Full test suite run leaves grader-events.jsonl unchanged

  REQ-LGT-003:
    title: Wrap _sv_llm_call gateway call in call_with_retry
    source_section: B.3 RC-2
    rationale: Adds 2-attempt retry + observability to primary LLM call path
    affected_files: [tools/supervisor/grade_declared_work.py]
    acceptance: Gateway transient failure triggers retry; grading events emitted; SDK fallback still fires on exhaustion

  REQ-LGT-004:
    title: Fix fallback detection in _sv_llm_call
    source_section: B.3 RC-5
    rationale: SDK fallback must fire unconditionally on any empty/failed gateway result
    affected_files: [tools/supervisor/grade_declared_work.py]
    acceptance: Exception in gateway call → SDK fallback is still attempted

  REQ-LGT-005:
    title: Wrap adversarial_check.py gateway call in call_with_retry
    source_section: B.3 RC-2
    rationale: Non-blocking adversarial scan gains retry without changing its non-blocking contract
    affected_files: [tools/supervisor/adversarial_check.py]
    acceptance: Transient gateway failure retried ≤2×; exhaustion returns {"status":"skipped"}

  REQ-LGT-006:
    title: Add CIRCUIT_OPEN error class to GraderErrorClass
    source_section: B.3 RC-3
    rationale: Needed to classify circuit-open fast-fail as a permanent error
    affected_files: [tools/supervisor/grader_reliability.py]
    acceptance: CIRCUIT_OPEN present in enum; classified as non-retryable

  REQ-LGT-007:
    title: Implement GraderCircuitBreaker
    source_section: B.3 RC-3
    rationale: Prevents retry storms when provider is completely down
    affected_files: [tools/supervisor/grader_reliability.py]
    acceptance: CLOSED→OPEN at 5 failures; OPEN→HALF_OPEN at 60s; HALF_OPEN→CLOSED on success

  REQ-LGT-008:
    title: Integrate circuit_breaker param into call_with_retry
    source_section: B.3 RC-3
    rationale: All grader calls automatically benefit from circuit breaker when one is provided
    affected_files: [tools/supervisor/grader_reliability.py]
    acceptance: OPEN circuit raises GraderPermanentFailure(CIRCUIT_OPEN) immediately

  REQ-LGT-009:
    title: Add max_age_minutes override to _get_cached_grade
    source_section: B.3 RC-4
    rationale: Enables short-TTL failure sentinel lookups separate from 7-day success cache
    affected_files: [tools/supervisor/grade_declared_work.py]
    acceptance: max_age_minutes param overrides 7-day default when provided

  REQ-LGT-010:
    title: Write failure sentinel cache entry on terminal fallback
    source_section: B.3 RC-4
    rationale: Makes same-sprint reruns consistent when LLM is unavailable
    affected_files: [tools/supervisor/grade_declared_work.py]
    acceptance: Terminal fallback writes fail:item_id cache entry; 30-min TTL; rerun returns cached

  REQ-LGT-011:
    title: Add tests REL-021 through REL-026
    source_section: Implementation Plan
    rationale: Covers CONNECTION_RESET, POOL_TIMEOUT, MALFORMED_RESPONSE, CANCELLED, circuit breaker
    affected_files: [tests/supervisor/test_grader_reliability.py]
    acceptance: All 6 new tests pass; all use tmp_path observers

  REQ-LGT-012:
    title: Pilot scripts for 8 fault scenarios
    source_section: Implementation Plan
    rationale: End-to-end proof that hardening works under controlled fault injection
    affected_files: [tools/supervisor/pilots/pilot_grader.py]
    acceptance: All 8 pilots exit 0
```

---

## [SECTION D] SOLUTION OPTIONS ANALYSIS

```yaml
# artifact_role: solution_options_analysis
# execution_authority: false

# For RC-1 (test log contamination), 3 options evaluated:

RC1_options:
  A_env_override:
    description: "Add GRADER_LOG_DIR env var; tests set it to tmp_path"
    scores:
      root_cause_coverage: 5
      production_durability: 5
      implementation_safety: 5
      testability: 5
      maintainability: 4
      regression_risk: 1  # (lowest = safest)
    verdict: SELECTED

  B_pytest_fixture_only:
    description: "Add conftest.py fixture that patches default log path for all tests"
    scores:
      root_cause_coverage: 4
      production_durability: 3  # doesn't help non-pytest callers
      implementation_safety: 4
      testability: 5
      maintainability: 3
      regression_risk: 2
    verdict: REJECTED — doesn't cover integration scripts outside pytest

  C_separate_log_file_per_process:
    description: "Use PID-stamped log files; aggregate separately"
    scores:
      root_cause_coverage: 3  # tests would still write to .local/
      production_durability: 3
      implementation_safety: 3
      testability: 3
      maintainability: 2
    verdict: REJECTED — doesn't solve the isolation problem

# For RC-2 (gateway has no retry):

RC2_options:
  A_wrap_in_call_with_retry:
    description: "Add call_with_retry block inside _sv_llm_call for gateway call"
    scores:
      root_cause_coverage: 5
      production_durability: 5
      rerun_consistency: 4
      implementation_safety: 4
      testability: 5
      maintainability: 5
    verdict: SELECTED

  B_move_retry_to_gateway_module:
    description: "Add retry inside gateway_chat() itself"
    scores:
      root_cause_coverage: 4
      implementation_safety: 2  # would require modifying tools/ai/ which has its own policies
      maintainability: 3
    verdict: REJECTED — gateway module is not owned by this plan

# For RC-3 (no circuit breaker):

RC3_options:
  A_process_level_circuit_breaker:
    description: "GraderCircuitBreaker class in grader_reliability.py"
    scores:
      root_cause_coverage: 4
      production_durability: 4
      implementation_safety: 5
      testability: 5
      maintainability: 4
    verdict: SELECTED

  B_file_backed_shared_breaker:
    description: "JSON file on disk as shared circuit state"
    scores:
      root_cause_coverage: 5
      production_durability: 5
      implementation_safety: 3  # race conditions on file writes
      testability: 3
      maintainability: 2
    verdict: DEFERRED — needed only for parallel sprint workers

# For RC-4 (failure not cached):

RC4_options:
  A_short_ttl_failure_sentinel:
    description: "Write fail:item_id cache entry with 30-min TTL at terminal fallback"
    scores:
      root_cause_coverage: 4
      rerun_consistency: 5
      implementation_safety: 5
      testability: 5
      maintainability: 4
    verdict: SELECTED

  B_cache_all_failures_with_long_ttl:
    description: "Cache all LLM failures indefinitely, force cache clear to retry"
    scores:
      rerun_consistency: 5
      production_durability: 2  # prevents LLM retry after provider recovers
      maintainability: 2
    verdict: REJECTED — would permanently suppress LLM grading after any outage
```

---

## [SECTION E] EXECUTION CONTROL LAYER

### Plan Outcome (Level 0)

`LLM_GRADER_TIMEOUT_HEALED_AND_PILOT_PROVEN`

Conditions for plan outcome:
- All 7 parent taskcards CLOSED
- All tests REL-001 through REL-026 pass
- Production log unchanged after full test run
- All 8 pilots exit 0
- No bare `except Exception` around any `gw(` call site

---

### Workstreams (Level 1)

- **WS-1** (TC-LGT-001): Observability — log isolation
- **WS-2** (TC-LGT-002 + TC-LGT-003): Retry coverage — gateway paths
- **WS-3** (TC-LGT-004): Reliability — circuit breaker
- **WS-4** (TC-LGT-005): Consistency — failure cache
- **WS-5** (TC-LGT-006): Test coverage — REL-021 to REL-026
- **WS-6** (TC-LGT-007): Validation — pilot proof

---

### Parent Taskcards (Level 2)

---

```
Parent Taskcard ID: TC-LGT-001
Title: Fix test observability isolation — stop tests polluting production log
Type: PARENT
Status: READY
Owner: reliability_agent
Supervisor: plan_supervisor

Source:
  Plan requirement ID: REQ-LGT-001, REQ-LGT-002
  Plan section: B.3 RC-1
  Root cause: Tests use default GradingObserver() which writes to .local/llm-call-logs/grader-events.jsonl
  Selected solution: Option A — GRADER_LOG_DIR env var + explicit tmp_path in all tests

Objective:
  - After this taskcard closes, a full test suite run must not modify grader-events.jsonl

Outcome:
  - grader_reliability.py respects GRADER_LOG_DIR env var for log path
  - All tests in test_grader_reliability.py use tmp_path-backed observers
  - Production log file hash unchanged after `pytest tests/supervisor/test_grader_reliability.py`

Scope:
  Allowed files:
    - tools/supervisor/grader_reliability.py
    - tests/supervisor/test_grader_reliability.py
  Forbidden files:
    - tools/supervisor/grade_declared_work.py  (TC-LGT-002 owns)
    - tools/supervisor/adversarial_check.py    (TC-LGT-003 owns)
    - Any other production source file
  Path expansion rule: No new files permitted; edit only the two listed files

Preserved behavior:
  - When GRADER_LOG_DIR is not set, default path is unchanged (.local/llm-call-logs/)
  - All REL-001 through REL-020 test logic (assertions) unchanged
  - GradingObserver() with explicit log_dir continues to work as before

Inputs:
  - grader_reliability.py (current _DEFAULT_LOG_DIR at line 283)
  - test_grader_reliability.py (all test classes REL-011 to REL-020)

Outputs:
  - grader_reliability.py with GRADER_LOG_DIR-aware _DEFAULT_LOG_DIR
  - test_grader_reliability.py with isolated observers in all tests
  - Evidence: grader-events.jsonl SHA-256 before and after test run (unchanged)

Dependencies:
  - None (first task; no prerequisites)

Child taskcards:
  - TC-LGT-001-01  (add GRADER_LOG_DIR to grader_reliability.py)
  - TC-LGT-001-02  (update all tests to use tmp_path observers)
  - TC-LGT-001-03  (verify production log unchanged)

Parent acceptance criteria:
  - TC-LGT-001-01 CLOSED with evidence
  - TC-LGT-001-02 CLOSED with evidence
  - TC-LGT-001-03 CLOSED with evidence
  - `pytest tests/supervisor/test_grader_reliability.py` exits 0
  - grader-events.jsonl hash before == hash after test run

Integration checks:
  - Import grader_reliability with GRADER_LOG_DIR set → log_dir uses env value
  - Import grader_reliability without GRADER_LOG_DIR → log_dir uses .local default

Evidence required:
  - SHA-256 of grader-events.jsonl before test run
  - SHA-256 of grader-events.jsonl after test run
  - pytest exit code and pass count for REL-001 to REL-020

Quality dimensions:
  - requirement correctness: env var overrides correctly
  - root-cause coverage: log contamination fully eliminated
  - regression safety: all existing tests still pass

Closeout criteria:
  - All 3 children CLOSED
  - Integration checks pass
  - No test writes to .local/llm-call-logs/ during test run

Rollback strategy:
  - git checkout -- tools/supervisor/grader_reliability.py tests/supervisor/test_grader_reliability.py

Stop conditions:
  - If GRADER_LOG_DIR env var conflicts with existing OS/CI var — raise BLOCKED, propose alternative name

Reroute rule:
  - Any failing child or hash mismatch reroutes that child only; re-execute from that child
```

---

```
Child Taskcard ID: TC-LGT-001-01
Parent Taskcard ID: TC-LGT-001
Title: Add GRADER_LOG_DIR environment variable override to grader_reliability.py
Type: CHILD
Status: TODO

Source:
  Plan requirement ID: REQ-LGT-001
  Plan section: B.3 RC-1; Implementation Plan TC-LGT-001
  Parent objective: Restore production log integrity by isolating test writes
  Root cause: _DEFAULT_LOG_DIR is a hardcoded module-level Path; tests cannot override it
  Selected solution: os.environ.get("GRADER_LOG_DIR", "") replaces hardcoded default

Purpose:
  - Makes the default log path configurable via environment variable so tests can redirect
    to tmp_path without touching production log

Scope:
  Allowed files:
    - tools/supervisor/grader_reliability.py
  Forbidden files: all others
  Required path decision: Change only lines 283-284 (the _DEFAULT_LOG_DIR definition)

Inputs:
  - Current grader_reliability.py lines 283-284:
    `_DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent.parent / ".local" / "llm-call-logs"`

Expected output:
  - Lines 283-285 (after edit):
    ```python
    _LOG_DIR_OVERRIDE = os.environ.get("GRADER_LOG_DIR", "")
    _DEFAULT_LOG_DIR = (
        Path(_LOG_DIR_OVERRIDE) if _LOG_DIR_OVERRIDE
        else Path(__file__).resolve().parent.parent.parent / ".local" / "llm-call-logs"
    )
    ```
  - `import os` must already be present at the top of the file (it is, line 19)

Preconditions:
  - grader_reliability.py has been read (required by Edit tool)

Micro-steps:
  - MS-LGT-001-01-01
  - MS-LGT-001-01-02
  - MS-LGT-001-01-03
  - MS-LGT-001-01-04
  - MS-LGT-001-01-05

Acceptance checks:
  - Edit produces no syntax error (python -c "import grader_reliability" passes with GRADER_LOG_DIR unset)
  - With GRADER_LOG_DIR=/tmp/test-logs, GradingObserver() creates log in /tmp/test-logs/
  - Without GRADER_LOG_DIR, GradingObserver() uses .local/llm-call-logs/

Evidence required:
  - Diff of changed lines
  - python -c "..." import test output

Rollback plan:
  - git checkout -- tools/supervisor/grader_reliability.py

Next valid task: TC-LGT-001-02
```

```
Micro-step ID: MS-LGT-001-01-01
Parent Taskcard ID: TC-LGT-001
Child Taskcard ID: TC-LGT-001-01
Status: PENDING
Action: Read grader_reliability.py lines 280-290 to capture current _DEFAULT_LOG_DIR definition exactly
Purpose: Establish the exact old_string for the Edit tool; prevent failed edit due to whitespace mismatch
Target:
  File: tools/supervisor/grader_reliability.py
  Symbol: _DEFAULT_LOG_DIR
  Lines: 283-284
Allowed operation: inspect
Forbidden operation: edit
Expected output: Exact text of lines 283-284 captured
Completion check: Text captured and matches what was read during planning
Next micro-step: MS-LGT-001-01-02
```

```
Micro-step ID: MS-LGT-001-01-02
Parent Taskcard ID: TC-LGT-001
Child Taskcard ID: TC-LGT-001-01
Status: PENDING
Action: Verify `import os` is present at line 19 of grader_reliability.py
Purpose: The new code uses os.environ.get; confirm no new import is needed
Target:
  File: tools/supervisor/grader_reliability.py
  Lines: 15-25
Allowed operation: inspect
Forbidden operation: edit
Expected output: Confirmation that `import os` exists
Failure handling: If not present, add `import os` to the import block (after `import json`)
Next micro-step: MS-LGT-001-01-03
```

```
Micro-step ID: MS-LGT-001-01-03
Parent Taskcard ID: TC-LGT-001
Child Taskcard ID: TC-LGT-001-01
Status: PENDING
Action: Edit grader_reliability.py — replace _DEFAULT_LOG_DIR with env-aware version
Purpose: Core change that enables test isolation via GRADER_LOG_DIR
Target:
  File: tools/supervisor/grader_reliability.py
  Symbol: _DEFAULT_LOG_DIR (line ~283)
Allowed operation: edit
old_string: |
  _DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent.parent / ".local" / "llm-call-logs"
new_string: |
  _LOG_DIR_OVERRIDE = os.environ.get("GRADER_LOG_DIR", "")
  _DEFAULT_LOG_DIR = (
      Path(_LOG_DIR_OVERRIDE) if _LOG_DIR_OVERRIDE
      else Path(__file__).resolve().parent.parent.parent / ".local" / "llm-call-logs"
  )
Forbidden operation: change any other line; change import block if os already imported
Expected output: Edit applied; surrounding lines unchanged
Next micro-step: MS-LGT-001-01-04
```

```
Micro-step ID: MS-LGT-001-01-04
Parent Taskcard ID: TC-LGT-001
Child Taskcard ID: TC-LGT-001-01
Status: PENDING
Action: Run syntax check — python -c "import sys; sys.path.insert(0,'tools/supervisor'); import grader_reliability; print('OK')"
Purpose: Confirm edit is valid Python; catch syntax errors before running full tests
Target: Command line (Bash tool)
Allowed operation: run
Expected output: "OK" printed; exit code 0
Failure handling: If syntax error, read error message, correct the edit (MS-LGT-001-01-03 retry), re-check
Next micro-step: MS-LGT-001-01-05
```

```
Micro-step ID: MS-LGT-001-01-05
Parent Taskcard ID: TC-LGT-001
Child Taskcard ID: TC-LGT-001-01
Status: PENDING
Action: Capture SHA-256 of .local/llm-call-logs/grader-events.jsonl as baseline
Purpose: Establish pre-test hash for comparison in TC-LGT-001-03
Target: .local/llm-call-logs/grader-events.jsonl
Allowed operation: run (hash command only)
Expected output: SHA-256 hex string recorded as evidence
Note: If file does not exist, record "FILE_ABSENT" as baseline
Completion check: Hash or FILE_ABSENT recorded
Next micro-step: TC-LGT-001-02 (next child)
```

---

```
Child Taskcard ID: TC-LGT-001-02
Parent Taskcard ID: TC-LGT-001
Title: Update all test_grader_reliability.py tests to use tmp_path-backed observers
Type: CHILD
Status: TODO

Source:
  Plan requirement ID: REQ-LGT-002
  Plan section: B.3 RC-1
  Parent objective: Full test suite run must not modify grader-events.jsonl

Purpose:
  - Prevent all existing REL-011 to REL-020 tests from writing to the production log

Scope:
  Allowed files:
    - tests/supervisor/test_grader_reliability.py
  Forbidden files: all production source
  Note: Test LOGIC (assertions) must not change — only observer construction changes

Affected tests (from prior read):
  - REL-011 (TestCallWithRetrySuccess): uses GradingObserver(log_dir=Path("/tmp/grader-test-obs")) → change to tmp_path
  - REL-012 (TestCallWithRetryTransient): call_with_retry has no explicit observer → add observer=GradingObserver(log_dir=tmp_path)
  - REL-013 (TestCallWithRetryExhausted): same
  - REL-015 (TestCallWithRetryDeadline): same (this is the source of 50000ms events)
  - REL-016 (TestCallWithRetryJitter): same
  - REL-017 (TestCallWithRetryRetryAfter): same
  - REL-020 (TestCallWithRetryObservability): uses FakeObserver (no log_dir needed) — verify no real observer used

Micro-steps:
  - MS-LGT-001-02-01
  - MS-LGT-001-02-02
  - MS-LGT-001-02-03
  - MS-LGT-001-02-04

Acceptance checks:
  - pytest tests/supervisor/test_grader_reliability.py exits 0
  - All REL-001 to REL-020 pass

Evidence required:
  - pytest output showing all tests pass
  - Confirmation that test assertions are unchanged (diff shows observer lines only)
```

```
Micro-step ID: MS-LGT-001-02-01
Child Taskcard ID: TC-LGT-001-02
Status: PENDING
Action: Read test_grader_reliability.py lines 269-280 (REL-011) and note exact observer construction
Purpose: Identify old_string for editing REL-011's hardcoded /tmp path
Allowed operation: inspect
Expected output: Exact text of observer construction in REL-011
Next micro-step: MS-LGT-001-02-02
```

```
Micro-step ID: MS-LGT-001-02-02
Child Taskcard ID: TC-LGT-001-02
Status: PENDING
Action: Edit REL-011 to convert test method to use tmp_path fixture
Purpose: Remove hardcoded /tmp path; use pytest's tmp_path for isolation
Allowed operation: edit
Note: REL-011's test class must gain `tmp_path` fixture param — add to method signature
      Change: `GradingObserver(log_dir=Path("/tmp/grader-test-obs"))` → `GradingObserver(log_dir=tmp_path)`
Forbidden: Change any assertion in the test
Expected output: REL-011 uses tmp_path; no hardcoded path remains
Next micro-step: MS-LGT-001-02-03
```

```
Micro-step ID: MS-LGT-001-02-03
Child Taskcard ID: TC-LGT-001-02
Status: PENDING
Action: Edit REL-012, REL-013, REL-015, REL-016, REL-017 — add explicit observer backed by tmp_path
Purpose: These tests call call_with_retry without an explicit observer, using the default
         which writes to production log
Strategy: Add `observer=GradingObserver(log_dir=tmp_path)` to each call_with_retry invocation
          Each test method gains `tmp_path` in its signature if not already present
Allowed operation: edit (one edit per test, or batch if edit tool allows)
Forbidden: Change any assertion or mock setup in the tests
Expected output: Each affected test passes an explicit observer
Next micro-step: MS-LGT-001-02-04
```

```
Micro-step ID: MS-LGT-001-02-04
Child Taskcard ID: TC-LGT-001-02
Status: PENDING
Action: Run pytest tests/supervisor/test_grader_reliability.py -v and capture output
Purpose: Confirm all REL-001 to REL-020 pass after observer changes
Allowed operation: run
Expected output: All 20 tests pass (exit 0)
Failure handling: If any test fails, read failure output; fix only the test observer change; re-run
Evidence: Full pytest -v output captured
Next micro-step: TC-LGT-001-03 (next child)
```

---

```
Child Taskcard ID: TC-LGT-001-03
Parent Taskcard ID: TC-LGT-001
Title: Verify production grader-events.jsonl is unchanged after full test run
Type: CHILD
Status: TODO

Purpose:
  - Prove that the observer isolation changes fully prevent log contamination

Micro-steps:
  - MS-LGT-001-03-01
  - MS-LGT-001-03-02
  - MS-LGT-001-03-03

Acceptance checks:
  - SHA-256 before == SHA-256 after
  - If file did not exist before, it still does not exist after (or was created only by production, not tests)
```

```
Micro-step ID: MS-LGT-001-03-01
Child Taskcard ID: TC-LGT-001-03
Status: PENDING
Action: Run full pytest tests/supervisor/test_grader_reliability.py suite (all tests)
Purpose: Trigger all test code paths that previously wrote to the production log
Allowed operation: run
Expected output: All tests pass (exit 0)
Next micro-step: MS-LGT-001-03-02
```

```
Micro-step ID: MS-LGT-001-03-02
Child Taskcard ID: TC-LGT-001-03
Status: PENDING
Action: Compute SHA-256 of .local/llm-call-logs/grader-events.jsonl post-run
Purpose: Compare with baseline hash from MS-LGT-001-01-05
Allowed operation: run (hash command)
Expected output: Hash matches baseline (or FILE_ABSENT matches FILE_ABSENT)
Failure handling: Hash mismatch → identify which test wrote to the log; add observer isolation to that test
Next micro-step: MS-LGT-001-03-03
```

```
Micro-step ID: MS-LGT-001-03-03
Child Taskcard ID: TC-LGT-001-03
Status: PENDING
Action: Record evidence — append before/after hashes to plan evidence section
Purpose: Proves TC-LGT-001 acceptance criterion (hash unchanged)
Allowed operation: record
Expected output: Evidence entry written with both hashes and verdict PASS/FAIL
Completion check: Evidence recorded; parent TC-LGT-001-03 can close
Next micro-step: (TC-LGT-001 integration check, then TC-LGT-002)
```

---

```
Parent Taskcard ID: TC-LGT-002
Title: Wrap _sv_llm_call gateway path in call_with_retry and fix fallback detection
Type: PARENT
Status: READY (depends on TC-LGT-001 being CLOSED — GRADER_LOG_DIR must exist first so new gateway events go to isolated log during tests)
Owner: reliability_agent

Source:
  Plan requirement ID: REQ-LGT-003, REQ-LGT-004
  Plan section: B.3 RC-2 and RC-5
  Root cause: Gateway call has no retry, no observability; fallback detection relies on fragile _record.status check
  Selected solution: Wrap _do_gateway() in call_with_retry; fallback unconditionally on empty content

Objective:
  - Add retry (max 2 attempts), observability (GradingEvent), and unconditional SDK fallback to the gateway path

Outcome:
  - Transient gateway failures emit grading events and retry before falling back to SDK
  - Any gateway failure (exception or empty) unconditionally invokes _sv_sdk_fallback

Scope:
  Allowed files:
    - tools/supervisor/grade_declared_work.py
  Forbidden files: all others
  Constraint: _sv_sdk_fallback must not be modified (TC-LGT-002 only modifies _sv_llm_call)

Preserved behavior:
  - _sv_sdk_fallback behavior unchanged
  - If reliability module not importable, bare try/except fallback preserved (graceful degradation)
  - Non-blocking: any failure still returns None (never raises to caller)

Dependencies:
  - TC-LGT-001-01 CLOSED (GRADER_LOG_DIR must exist for test isolation when testing this change)

Child taskcards:
  - TC-LGT-002-01  (add lazy reliability import block to _sv_llm_call)
  - TC-LGT-002-02  (define _do_gateway closure)
  - TC-LGT-002-03  (wrap _do_gateway in call_with_retry or bare try)
  - TC-LGT-002-04  (restructure return path — unconditional SDK fallback)
  - TC-LGT-002-05  (add integration test: gateway transient → retry → SDK fallback)

Parent acceptance criteria:
  - Gateway transient exception → 2 retry attempts → grading events emitted → SDK fallback invoked
  - Gateway empty response (any reason) → SDK fallback invoked (not silent None)
  - _sv_sdk_fallback behavior unchanged
  - All existing REL-011 to REL-020 still pass

Rollback strategy:
  - git checkout -- tools/supervisor/grade_declared_work.py
```

```
Child Taskcard ID: TC-LGT-002-01
Parent Taskcard ID: TC-LGT-002
Title: Read _sv_llm_call current implementation and record exact function body
Type: CHILD
Status: TODO

Purpose:
  - Establish the exact current text of _sv_llm_call before any edits
  - Required by Edit tool (must read before editing)

Micro-steps:
  - MS-LGT-002-01-01

Acceptance checks:
  - _sv_llm_call lines 227-256 captured and verified
```

```
Micro-step ID: MS-LGT-002-01-01
Child Taskcard ID: TC-LGT-002-01
Status: PENDING
Action: Read grade_declared_work.py lines 227-260 and record the full _sv_llm_call body
Purpose: Required baseline before editing; captures exact whitespace/indentation
Allowed operation: inspect
Expected output: Exact text of _sv_llm_call captured
Next micro-step: TC-LGT-002-02 (proceed to edit child)
```

```
Child Taskcard ID: TC-LGT-002-02
Parent Taskcard ID: TC-LGT-002
Title: Add lazy reliability module import block inside _sv_llm_call
Type: CHILD
Status: TODO

Purpose:
  - Enables call_with_retry use without a hard import-time dependency
  - Same pattern already used in _sv_sdk_fallback (grade_declared_work.py:276-290)

Scope:
  Allowed files: tools/supervisor/grade_declared_work.py
  Constraint: Lazy import block must be inside _sv_llm_call body, after the gw=None guard

Micro-steps:
  - MS-LGT-002-02-01

Acceptance checks:
  - When grader_reliability not importable, _rel_ok = False without crash
  - When importable, RetryPolicy, GradingObserver, call_with_retry, exceptions are available
```

```
Micro-step ID: MS-LGT-002-02-01
Child Taskcard ID: TC-LGT-002-02
Status: PENDING
Action: Edit _sv_llm_call — insert lazy import block after the `if gw is None: return None` guard
Purpose: Add reliability imports to gateway call path
Target:
  File: tools/supervisor/grade_declared_work.py
  Location: Inside _sv_llm_call, after line "if gw is None: ..." block
Insert block (exact indentation must match surrounding code — 4 spaces):
  ```
  try:
      from grader_reliability import (
          RetryPolicy, GradingObserver, call_with_retry,
          GraderRetryExhausted, GraderPermanentFailure,
      )
      _rel_ok = True
  except ImportError:
      try:
          from tools.supervisor.grader_reliability import (
              RetryPolicy, GradingObserver, call_with_retry,
              GraderRetryExhausted, GraderPermanentFailure,
          )
          _rel_ok = True
      except ImportError:
          _rel_ok = False
  ```
Forbidden: Change any other line
Expected output: Import block inserted; surrounding code unchanged
Next micro-step: TC-LGT-002-03 (next child)
```

```
Child Taskcard ID: TC-LGT-002-03
Parent Taskcard ID: TC-LGT-002
Title: Define _do_gateway closure and wrap in call_with_retry (or bare try if _rel_ok=False)
Type: CHILD
Status: TODO

Purpose:
  - Turns the gateway call into a zero-arg callable suitable for call_with_retry
  - Provides retry + observability for gateway path

Micro-steps:
  - MS-LGT-002-03-01
  - MS-LGT-002-03-02

Acceptance checks:
  - _do_gateway() raises for non-success, returns string content for success
  - call_with_retry invoked with RetryPolicy(max_attempts=2, overall_deadline=45.0)
  - On GraderRetryExhausted or GraderPermanentFailure: content = "" (not raised to caller)
```

```
Micro-step ID: MS-LGT-002-03-01
Child Taskcard ID: TC-LGT-002-03
Status: PENDING
Action: Replace the current `try: resp, _record = gw(...) ... except Exception: return None` block
        with the new _do_gateway closure definition
Purpose: Encapsulates gateway call as zero-arg callable
Target:
  File: tools/supervisor/grade_declared_work.py
  Symbol: _sv_llm_call body, current try/except block (lines ~236-256)
Replace with:
  ```
  def _do_gateway() -> str:
      resp, _ = gw(config=cfg, model="recommended", messages=messages,
                   role="evidence_review", operation=operation)
      return resp.get("content", "")

  if _rel_ok:
      _gw_policy = RetryPolicy(
          max_attempts=2,
          base_backoff=2.0,
          jitter=True,
          overall_deadline=45.0,
          connect_timeout=10.0,
          read_timeout=20.0,
      )
      _gw_observer = GradingObserver()
      try:
          content = call_with_retry(
              _do_gateway,
              policy=_gw_policy,
              observer=_gw_observer,
              item_id=item_id,
              provider="gateway",
              model="recommended",
          )
      except (GraderPermanentFailure, GraderRetryExhausted):
          content = ""
      except Exception:
          content = ""
  else:
      try:
          content = _do_gateway()
      except Exception:
          content = ""
  ```
Forbidden: Change function signature, docstring, or any line outside this block
Next micro-step: MS-LGT-002-03-02
```

```
Micro-step ID: MS-LGT-002-03-02
Child Taskcard ID: TC-LGT-002-03
Status: PENDING
Action: Verify syntax — python -c "import sys; sys.path.insert(0,'tools/supervisor'); import grade_declared_work; print('OK')"
Purpose: Confirm edit is valid Python
Allowed operation: run
Expected output: "OK" (exit 0)
Failure handling: Read error, fix edit, re-verify
Next micro-step: TC-LGT-002-04 (next child)
```

```
Child Taskcard ID: TC-LGT-002-04
Parent Taskcard ID: TC-LGT-002
Title: Restructure _sv_llm_call return path — unconditional SDK fallback
Type: CHILD
Status: TODO

Purpose:
  - Replace fragile _record.status check with: if content → return content; else → SDK fallback
  - Ensures SDK fallback fires for ANY gateway failure (exception, empty, blocked_missing_env)

Micro-steps:
  - MS-LGT-002-04-01

Acceptance checks:
  - gateway returns empty → SDK fallback invoked
  - gateway raises exception → content="" → SDK fallback invoked
  - gateway returns content → returned directly, SDK fallback NOT invoked
```

```
Micro-step ID: MS-LGT-002-04-01
Child Taskcard ID: TC-LGT-002-04
Status: PENDING
Action: Replace the end of _sv_llm_call (after the call_with_retry block) with:
  ```
  if content:
      return content
  # Gateway failed or returned empty — fall through to SDK unconditionally
  return _sv_sdk_fallback(messages, cfg, item_id=item_id)
  ```
Target: grade_declared_work.py — end of _sv_llm_call after the if _rel_ok / else block
Remove: The old `if _record and ... "error" in ... _sv_sdk_fallback` check
Forbidden: Change _sv_sdk_fallback function
Expected output: _sv_sdk_fallback called whenever content is falsy
Next micro-step: TC-LGT-002-05 (verification child)
```

```
Child Taskcard ID: TC-LGT-002-05
Parent Taskcard ID: TC-LGT-002
Title: Run REL-001 to REL-020 regression test after TC-LGT-002 edits
Type: CHILD
Status: TODO

Purpose:
  - Verify that _sv_llm_call changes did not break any existing test

Micro-steps:
  - MS-LGT-002-05-01
  - MS-LGT-002-05-02

Acceptance checks:
  - pytest exits 0
  - All 20 REL tests pass
  - grader-events.jsonl hash unchanged (confirming TC-LGT-001 still works)
```

```
Micro-step ID: MS-LGT-002-05-01
Child Taskcard ID: TC-LGT-002-05
Status: PENDING
Action: Run .venv/Scripts/pytest tests/supervisor/test_grader_reliability.py -v
Purpose: Regression check
Allowed operation: run
Expected output: All REL-001 to REL-020 pass
Failure handling: Read failure; determine if failure is from TC-LGT-002 edit or pre-existing; fix TC-LGT-002 edit only
Next micro-step: MS-LGT-002-05-02
```

```
Micro-step ID: MS-LGT-002-05-02
Child Taskcard ID: TC-LGT-002-05
Status: PENDING
Action: Record TC-LGT-002 evidence — pytest output + diff of grade_declared_work.py
Purpose: Evidence for parent TC-LGT-002 acceptance criteria
Allowed operation: record
Next micro-step: TC-LGT-003 (next parent)
```

---

```
Parent Taskcard ID: TC-LGT-003
Title: Wrap adversarial_check.py gateway call in call_with_retry
Type: PARENT
Status: READY (depends on TC-LGT-001 CLOSED)
Owner: reliability_agent

Source:
  Plan requirement ID: REQ-LGT-005
  Plan section: B.3 RC-2
  Root cause: adversarial_check.py:63-70 bare except swallows all gateway errors

Objective:
  - Add 2-attempt retry to adversarial gateway call without changing non-blocking contract

Preserved behavior:
  - ALL failure paths still return {"status": "skipped", "reason": "..."}
  - Non-blocking contract: never raises to caller

Dependencies:
  - TC-LGT-001 CLOSED (for log isolation during testing)
  - TC-LGT-002 CLOSED (establishes the pattern to replicate here)

Child taskcards:
  - TC-LGT-003-01  (read adversarial_check.py gw() call, add lazy import + call_with_retry)
  - TC-LGT-003-02  (verify non-blocking contract preserved)

Parent acceptance criteria:
  - Transient gateway error in adversarial_check retried ≤2×; grading events emitted
  - All failures return {"status": "skipped"} — never raises
```

```
Child Taskcard ID: TC-LGT-003-01
Parent Taskcard ID: TC-LGT-003
Title: Add lazy reliability import and call_with_retry to adversarial_check.py run_adversarial_check
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-003-01-01
  - MS-LGT-003-01-02
  - MS-LGT-003-01-03

Scope:
  Allowed files: tools/supervisor/adversarial_check.py
  Constraint: non-blocking contract preserved; all error paths return dict not raise
```

```
Micro-step ID: MS-LGT-003-01-01
Child Taskcard ID: TC-LGT-003-01
Status: PENDING
Action: Read adversarial_check.py lines 60-74 to capture current gw() call and exception handler
Allowed operation: inspect
Next micro-step: MS-LGT-003-01-02
```

```
Micro-step ID: MS-LGT-003-01-02
Child Taskcard ID: TC-LGT-003-01
Status: PENDING
Action: Edit run_adversarial_check — add lazy reliability import block + wrap gw() in call_with_retry
Purpose: Same pattern as TC-LGT-002-02/03 but with max_attempts=2, overall_deadline=30.0
Pattern to insert (inside run_adversarial_check, after gw/cfg obtained):
  - Lazy import block identical to TC-LGT-002-02 pattern
  - Define _do_adversarial() closure: `response, _ = gw(messages=messages); return response.get("content","")`
  - If _rel_ok: wrap in call_with_retry(policy=RetryPolicy(max_attempts=2, overall_deadline=30.0))
  - On GraderRetryExhausted/GraderPermanentFailure/Exception: return {"status": "skipped", "reason": ...}
  - If not _rel_ok: bare try/except (existing behavior)
Forbidden: Change any code outside run_adversarial_check
Next micro-step: MS-LGT-003-01-03
```

```
Micro-step ID: MS-LGT-003-01-03
Child Taskcard ID: TC-LGT-003-01
Status: PENDING
Action: Verify syntax — python -c "import sys; sys.path.insert(0,'tools/supervisor'); import adversarial_check; print('OK')"
Allowed operation: run
Expected output: "OK"
Next micro-step: TC-LGT-003-02
```

```
Child Taskcard ID: TC-LGT-003-02
Parent Taskcard ID: TC-LGT-003
Title: Verify adversarial_check non-blocking contract preserved
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-003-02-01

Acceptance checks:
  - run_adversarial_check with no gw configured → {"status":"skipped"}
  - run_adversarial_check with gw raising exception → {"status":"skipped", "reason":"retry_exhausted"} or similar
  - Never raises
```

```
Micro-step ID: MS-LGT-003-02-01
Child Taskcard ID: TC-LGT-003-02
Status: PENDING
Action: Run python -c that calls run_adversarial_check with a mock gw that raises
        Verify return value is a dict with status="skipped"
Target: adversarial_check.py, run_adversarial_check function
Allowed operation: run (inline test only)
Next micro-step: TC-LGT-004 (next parent)
```

---

```
Parent Taskcard ID: TC-LGT-004
Title: Add GraderCircuitBreaker to grader_reliability.py
Type: PARENT
Status: READY (depends on TC-LGT-001 CLOSED)
Owner: reliability_agent

Source:
  Plan requirement ID: REQ-LGT-006, REQ-LGT-007, REQ-LGT-008
  Plan section: B.3 RC-3
  Root cause: No circuit breaker → provider outage causes unbounded retry storms

Objective:
  - Add process-level CLOSED/OPEN/HALF_OPEN circuit breaker integrated into call_with_retry

Preserved behavior:
  - call_with_retry behavior unchanged when circuit_breaker=None (default)
  - All existing tests continue to pass without modification

Dependencies:
  - TC-LGT-001 CLOSED

Child taskcards:
  - TC-LGT-004-01  (add CIRCUIT_OPEN to GraderErrorClass + _NON_RETRYABLE set)
  - TC-LGT-004-02  (implement CircuitState enum + GraderCircuitBreaker class)
  - TC-LGT-004-03  (add circuit_breaker param to call_with_retry)
  - TC-LGT-004-04  (add module-level default breaker + get_default_circuit_breaker())
  - TC-LGT-004-05  (verify call_with_retry backward-compat — circuit_breaker=None default)

Parent acceptance criteria:
  - 5 consecutive record_failure() calls → is_open() returns True
  - After 60s (fake_monotonic), is_open() returns False (probe)
  - probe success → record_success() → is_open() returns False (CLOSED)
  - call_with_retry with OPEN breaker → raises GraderPermanentFailure(CIRCUIT_OPEN) on first attempt
  - call_with_retry without breaker (None) → behaves exactly as before

Rollback strategy:
  - git checkout -- tools/supervisor/grader_reliability.py
```

```
Child Taskcard ID: TC-LGT-004-01
Parent Taskcard ID: TC-LGT-004
Title: Add CIRCUIT_OPEN to GraderErrorClass and _NON_RETRYABLE set
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-004-01-01
  - MS-LGT-004-01-02
```

```
Micro-step ID: MS-LGT-004-01-01
Child Taskcard ID: TC-LGT-004-01
Status: PENDING
Action: Read grader_reliability.py lines 36-75 (GraderErrorClass enum + _RETRYABLE/_NON_RETRYABLE)
Allowed operation: inspect
Next micro-step: MS-LGT-004-01-02
```

```
Micro-step ID: MS-LGT-004-01-02
Child Taskcard ID: TC-LGT-004-01
Status: PENDING
Action: Edit grader_reliability.py — add CIRCUIT_OPEN = "CIRCUIT_OPEN" to GraderErrorClass
        AND add GraderErrorClass.CIRCUIT_OPEN to _NON_RETRYABLE frozenset
Target:
  - Line after UNKNOWN_PROVIDER_FAILURE in GraderErrorClass: add CIRCUIT_OPEN = "CIRCUIT_OPEN"
  - In _NON_RETRYABLE set: add GraderErrorClass.CIRCUIT_OPEN
Forbidden: Change any other enum value or set member
Next micro-step: TC-LGT-004-02
```

```
Child Taskcard ID: TC-LGT-004-02
Parent Taskcard ID: TC-LGT-004
Title: Implement CircuitState enum and GraderCircuitBreaker class
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-004-02-01
  - MS-LGT-004-02-02

Scope:
  Allowed files: tools/supervisor/grader_reliability.py
  Insert location: After RetryPolicy dataclass (around line 263)
  threading import: Add `import threading` to imports if not present
```

```
Micro-step ID: MS-LGT-004-02-01
Child Taskcard ID: TC-LGT-004-02
Status: PENDING
Action: Check if `import threading` is in grader_reliability.py imports
Allowed operation: inspect (lines 1-30)
Expected output: threading import present or absent (record finding)
Failure handling: If absent, add `import threading` after `import time` in import block
Next micro-step: MS-LGT-004-02-02
```

```
Micro-step ID: MS-LGT-004-02-02
Child Taskcard ID: TC-LGT-004-02
Status: PENDING
Action: Insert CircuitState enum and GraderCircuitBreaker dataclass after RetryPolicy class
Purpose: Core circuit breaker implementation
Insert after `RetryPolicy.backoff_for` method:
  ```python
  class CircuitState(str, Enum):
      CLOSED = "CLOSED"
      OPEN = "OPEN"
      HALF_OPEN = "HALF_OPEN"

  @dataclass
  class GraderCircuitBreaker:
      failure_threshold: int = 5
      reset_timeout: float = 60.0
      _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
      _consecutive_failures: int = field(default=0, init=False)
      _opened_at: "float | None" = field(default=None, init=False)
      _lock: "threading.Lock" = field(default_factory=threading.Lock, init=False)

      def is_open(self) -> bool:
          with self._lock:
              if self._state == CircuitState.CLOSED:
                  return False
              if self._state == CircuitState.OPEN:
                  if time.monotonic() - (self._opened_at or 0) >= self.reset_timeout:
                      self._state = CircuitState.HALF_OPEN
                      return False
                  return True
              return False  # HALF_OPEN: allow one probe

      def record_success(self) -> None:
          with self._lock:
              self._consecutive_failures = 0
              self._state = CircuitState.CLOSED
              self._opened_at = None

      def record_failure(self) -> None:
          with self._lock:
              self._consecutive_failures += 1
              if (self._state == CircuitState.HALF_OPEN or
                      self._consecutive_failures >= self.failure_threshold):
                  self._state = CircuitState.OPEN
                  self._opened_at = time.monotonic()
  ```
Forbidden: Change RetryPolicy, GradingEvent, GradingObserver, call_with_retry (yet)
Next micro-step: TC-LGT-004-03
```

```
Child Taskcard ID: TC-LGT-004-03
Parent Taskcard ID: TC-LGT-004
Title: Add circuit_breaker parameter to call_with_retry and integrate CIRCUIT_OPEN logic
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-004-03-01
  - MS-LGT-004-03-02

Scope:
  Allowed files: tools/supervisor/grader_reliability.py
  Target function: call_with_retry (lines ~350-459)
  Constraint: When circuit_breaker=None (default), function must behave identically to current
```

```
Micro-step ID: MS-LGT-004-03-01
Child Taskcard ID: TC-LGT-004-03
Status: PENDING
Action: Read call_with_retry signature and first 20 lines to capture exact text for edit
Allowed operation: inspect
Next micro-step: MS-LGT-004-03-02
```

```
Micro-step ID: MS-LGT-004-03-02
Child Taskcard ID: TC-LGT-004-03
Status: PENDING
Action: Edit call_with_retry:
  1. Add `circuit_breaker: "GraderCircuitBreaker | None" = None` to function signature
  2. At the start of each attempt's try block (before `result = fn()`), insert:
     ```python
     if circuit_breaker is not None and circuit_breaker.is_open():
         raise GraderPermanentFailure(
             GraderErrorClass.CIRCUIT_OPEN,
             RuntimeError("circuit breaker is OPEN")
         )
     ```
  3. After `result = fn()` succeeds, before return: `if circuit_breaker: circuit_breaker.record_success()`
  4. In the `except Exception as exc:` block, after `cls = classify_exception(exc)`:
     `if circuit_breaker and is_retryable(cls): circuit_breaker.record_failure()`
Forbidden: Change any other logic; change default values of existing parameters
Expected output: circuit_breaker=None path is identical to current behavior
Next micro-step: TC-LGT-004-04
```

```
Child Taskcard ID: TC-LGT-004-04
Parent Taskcard ID: TC-LGT-004
Title: Add module-level default circuit breaker and get_default_circuit_breaker()
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-004-04-01
```

```
Micro-step ID: MS-LGT-004-04-01
Child Taskcard ID: TC-LGT-004-04
Status: PENDING
Action: After _get_default_observer() (line ~327), insert:
  ```python
  _default_circuit_breaker: "GraderCircuitBreaker | None" = None

  def get_default_circuit_breaker() -> "GraderCircuitBreaker":
      global _default_circuit_breaker
      if _default_circuit_breaker is None:
          _default_circuit_breaker = GraderCircuitBreaker()
      return _default_circuit_breaker

  def reset_default_circuit_breaker() -> None:
      """Force-close the process-level circuit breaker. Call to recover from OPEN state."""
      global _default_circuit_breaker
      _default_circuit_breaker = None
  ```
Forbidden: Change GradingObserver or _get_default_observer
Next micro-step: TC-LGT-004-05
```

```
Child Taskcard ID: TC-LGT-004-05
Parent Taskcard ID: TC-LGT-004
Title: Syntax check and import test for grader_reliability.py after all circuit breaker edits
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-004-05-01
  - MS-LGT-004-05-02
```

```
Micro-step ID: MS-LGT-004-05-01
Child Taskcard ID: TC-LGT-004-05
Status: PENDING
Action: python -c "import sys; sys.path.insert(0,'tools/supervisor'); import grader_reliability; b=grader_reliability.GraderCircuitBreaker(); print(b.is_open(), 'OK')"
Expected output: "False OK"
Failure handling: Fix syntax/logic error, re-run
Next micro-step: MS-LGT-004-05-02
```

```
Micro-step ID: MS-LGT-004-05-02
Child Taskcard ID: TC-LGT-004-05
Status: PENDING
Action: Run .venv/Scripts/pytest tests/supervisor/test_grader_reliability.py -v (REL-001 to REL-020)
Purpose: Backward-compatibility regression check
Expected output: All existing tests pass
Next micro-step: TC-LGT-005 (next parent)
```

---

```
Parent Taskcard ID: TC-LGT-005
Title: Add short-TTL failure sentinel cache to prevent rerun inconsistency
Type: PARENT
Status: READY (depends on TC-LGT-001 CLOSED)
Owner: reliability_agent

Source:
  Plan requirement ID: REQ-LGT-009, REQ-LGT-010
  Plan section: B.3 RC-4
  Root cause: Terminal fallback in semantic_verify_item is not cached; rerun gets different grade

Objective:
  - Terminal fallback writes a 30-minute sentinel; same-sprint reruns return consistent grade

Dependencies:
  - TC-LGT-001 CLOSED

Child taskcards:
  - TC-LGT-005-01  (add max_age_minutes param to _get_cached_grade)
  - TC-LGT-005-02  (add failure sentinel write at terminal fallback)
  - TC-LGT-005-03  (add failure sentinel read check at top of semantic_verify_item)
  - TC-LGT-005-04  (test: failure cached, rerun returns cache, TTL expiry re-attempts)

Preserved behavior:
  - Success cache (7-day TTL) unchanged
  - iv: prefix cache unchanged
  - After 30 min, LLM IS retried (not permanently suppressed)

Rollback strategy:
  - git checkout -- tools/supervisor/grade_declared_work.py
```

```
Child Taskcard ID: TC-LGT-005-01
Parent Taskcard ID: TC-LGT-005
Title: Add optional max_age_minutes parameter to _get_cached_grade
Type: CHILD
Status: TODO

Purpose:
  - Allows failure sentinel lookups to use a short TTL without changing the 7-day default

Micro-steps:
  - MS-LGT-005-01-01
  - MS-LGT-005-01-02

Scope:
  Allowed files: tools/supervisor/grade_declared_work.py
  Target: _get_cached_grade function (lines 67-91)
  Constraint: Default behavior (no max_age_minutes) must not change
```

```
Micro-step ID: MS-LGT-005-01-01
Child Taskcard ID: TC-LGT-005-01
Status: PENDING
Action: Read _get_cached_grade lines 67-91 to capture exact signature and TTL logic
Allowed operation: inspect
Next micro-step: MS-LGT-005-01-02
```

```
Micro-step ID: MS-LGT-005-01-02
Child Taskcard ID: TC-LGT-005-01
Status: PENDING
Action: Edit _get_cached_grade:
  1. Add `max_age_minutes: "int | None" = None` to function signature
  2. Change TTL check logic:
     ```python
     _MAX_CACHE_AGE_DAYS = 7
     if max_age_minutes is not None:
         max_age_seconds = max_age_minutes * 60
         age_seconds = (datetime.now(timezone.utc) - datetime.fromisoformat(cached_at)).total_seconds()
         if age_seconds > max_age_seconds:
             return None
     else:
         age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached_at)).days
         if age > _MAX_CACHE_AGE_DAYS:
             return None
     ```
Forbidden: Change any other caller or the function's exception handling
Next micro-step: TC-LGT-005-02
```

```
Child Taskcard ID: TC-LGT-005-02
Parent Taskcard ID: TC-LGT-005
Title: Write failure sentinel cache entry at terminal fallback in semantic_verify_item
Type: CHILD
Status: TODO

Purpose:
  - Makes the terminal fallback result reproducible within the 30-minute TTL window

Micro-steps:
  - MS-LGT-005-02-01
```

```
Micro-step ID: MS-LGT-005-02-01
Child Taskcard ID: TC-LGT-005-02
Status: PENDING
Action: Edit semantic_verify_item — replace terminal fallback return (lines 487-489) with:
  ```python
  _FAILURE_TTL_MINUTES = 30
  _fail_result = {
      "adequate": False, "confidence": 0.0, "stub_detected": False,
      "deficiencies": ["llm_verification_unavailable"], "llm_used": False,
      "source": "fallback_llm_unavailable",
      "_failure_cached": True,
      "_failure_ttl_minutes": _FAILURE_TTL_MINUTES,
  }
  # Add per-item jitter (0–5 min) to spread write spike after outage recovery
  import random as _random
  _jitter = _random.randint(0, 5)
  _effective_ttl = _FAILURE_TTL_MINUTES + _jitter
  _fail_result["_failure_ttl_minutes"] = _effective_ttl
  _cache_grade(f"fail:{item_id}", ev_hash, _fail_result, cache_path=cache_path)
  return _fail_result
  ```
Note: `import random as _random` should be done at top of file, not inside the function.
      Check if random is already imported; if so, use the existing import name.
Forbidden: Change the iv: cache path or success cache path
Next micro-step: TC-LGT-005-03
```

```
Child Taskcard ID: TC-LGT-005-03
Parent Taskcard ID: TC-LGT-005
Title: Add failure sentinel read check at top of semantic_verify_item (after success cache check)
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-005-03-01
```

```
Micro-step ID: MS-LGT-005-03-01
Child Taskcard ID: TC-LGT-005-03
Status: PENDING
Action: Edit semantic_verify_item — after the existing `if cached is not None: return` block
        (line ~388), insert:
  ```python
  # Failure sentinel check: if LLM failed recently, return cached failure for consistency
  _fail_sentinel = _get_cached_grade(
      f"fail:{item_id}", ev_hash, cache_path=cache_path, max_age_minutes=30
  )
  if _fail_sentinel is not None:
      return {**_fail_sentinel, "_from_cache": True}
  ```
Constraint: This check must come AFTER the success cache check and BEFORE the evidence path check
Forbidden: Change success cache check or evidence path logic
Next micro-step: TC-LGT-005-04
```

```
Child Taskcard ID: TC-LGT-005-04
Parent Taskcard ID: TC-LGT-005
Title: Verify failure sentinel caching with focused inline test
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-005-04-01
```

```
Micro-step ID: MS-LGT-005-04-01
Child Taskcard ID: TC-LGT-005-04
Status: PENDING
Action: Run python inline test to verify failure sentinel behavior:
  ```python
  python -c "
  import sys, os, tempfile
  sys.path.insert(0,'tools/supervisor')
  os.environ['GRADER_LOG_DIR'] = tempfile.mkdtemp()
  from grade_declared_work import _get_cached_grade, _cache_grade
  import tempfile, pathlib
  tmp = pathlib.Path(tempfile.mkdtemp())
  cache = tmp / 'cache.json'
  item_id = 'test-item'
  ev_hash = 'abc123'
  result = {'adequate': False, '_failure_cached': True, '_failure_ttl_minutes': 30}
  _cache_grade(f'fail:{item_id}', ev_hash, result, cache_path=cache)
  hit = _get_cached_grade(f'fail:{item_id}', ev_hash, cache_path=cache, max_age_minutes=30)
  assert hit is not None, 'FAIL: cache miss expected hit'
  print('PASS: failure sentinel cached and retrieved')
  "
  ```
Expected output: "PASS: failure sentinel cached and retrieved"
Failure handling: Read error, fix code, re-run
Next micro-step: TC-LGT-006 (next parent)
```

---

```
Parent Taskcard ID: TC-LGT-006
Title: Add tests REL-021 through REL-026 to test_grader_reliability.py
Type: PARENT
Status: READY (depends on TC-LGT-001 CLOSED, TC-LGT-004 CLOSED for REL-025/026)
Owner: reliability_agent

Source:
  Plan requirement ID: REQ-LGT-011
  Plan section: Implementation Plan TC-LGT-006

Objective:
  - Cover 6 missing test scenarios: CONNECTION_RESET, POOL_TIMEOUT, MALFORMED_RESPONSE,
    CANCELLED (KeyboardInterrupt), circuit breaker opens, circuit breaker closes

Dependencies:
  - TC-LGT-001 CLOSED (tmp_path observers required)
  - TC-LGT-004 CLOSED (GraderCircuitBreaker must exist for REL-025/026)

Child taskcards:
  - TC-LGT-006-01  (REL-021: RemoteProtocolError → CONNECTION_RESET)
  - TC-LGT-006-02  (REL-022: PoolTimeout → POOL_TIMEOUT, retried, exhausted)
  - TC-LGT-006-03  (REL-023: MALFORMED_RESPONSE → non-retryable)
  - TC-LGT-006-04  (REL-024: KeyboardInterrupt → CANCELLED + GraderPermanentFailure)
  - TC-LGT-006-05  (REL-025: GraderCircuitBreaker opens after 5 failures)
  - TC-LGT-006-06  (REL-026: Circuit HALF_OPEN → probe success → CLOSED)
  - TC-LGT-006-07  (run all REL-001 to REL-026, confirm all pass)

Parent acceptance criteria:
  - All 6 new tests pass
  - All existing REL-001 to REL-020 still pass
  - All tests use tmp_path observers
```

```
Child Taskcard ID: TC-LGT-006-01
Parent Taskcard ID: TC-LGT-006
Title: Add REL-021 — RemoteProtocolError → CONNECTION_RESET classification
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-006-01-01
```

```
Micro-step ID: MS-LGT-006-01-01
Child Taskcard ID: TC-LGT-006-01
Status: PENDING
Action: Append TestClassifyExceptionConnectionReset class to test_grader_reliability.py:
  ```python
  class TestClassifyExceptionConnectionReset:
      def test_remote_protocol_error_connection_reset(self):
          """REL-021: RemoteProtocolError → CONNECTION_RESET."""
          exc = _make_exc("RemoteProtocolError", "peer closed connection")
          assert classify_exception(exc) == GraderErrorClass.CONNECTION_RESET

      def test_connection_reset_is_retryable(self):
          """REL-021b: CONNECTION_RESET is retryable."""
          assert is_retryable(GraderErrorClass.CONNECTION_RESET) is True
  ```
Forbidden: Change any existing test class
Next micro-step: TC-LGT-006-02
```

```
Child Taskcard ID: TC-LGT-006-02
Parent Taskcard ID: TC-LGT-006
Title: Add REL-022 — PoolTimeout → POOL_TIMEOUT, retry, exhaustion
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-006-02-01
```

```
Micro-step ID: MS-LGT-006-02-01
Child Taskcard ID: TC-LGT-006-02
Status: PENDING
Action: Append TestClassifyExceptionPoolTimeout class:
  ```python
  class TestCallWithRetryPoolTimeout:
      def test_pool_timeout_retried_then_exhausted(self, tmp_path):
          """REL-022: PoolTimeout retried then GraderRetryExhausted."""
          calls = [0]
          def fn():
              calls[0] += 1
              raise _make_exc("PoolTimeout", "connection pool exhausted")
          policy = RetryPolicy(max_attempts=3, base_backoff=0.01, jitter=False, overall_deadline=10.0)
          observer = GradingObserver(log_dir=tmp_path)
          with patch("grader_reliability.time.sleep"):
              try:
                  call_with_retry(fn, policy=policy, observer=observer)
                  assert False, "Should have raised"
              except GraderRetryExhausted as exc:
                  assert exc.error_class == GraderErrorClass.POOL_TIMEOUT
          assert calls[0] == 3
  ```
Next micro-step: TC-LGT-006-03
```

```
Child Taskcard ID: TC-LGT-006-03
Parent Taskcard ID: TC-LGT-006
Title: Add REL-023 — MALFORMED_RESPONSE is non-retryable
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-006-03-01
```

```
Micro-step ID: MS-LGT-006-03-01
Child Taskcard ID: TC-LGT-006-03
Status: PENDING
Action: Append TestMalformedResponse class:
  ```python
  class TestMalformedResponse:
      def test_json_decode_error_permanent(self, tmp_path):
          """REL-023: json decode message → MALFORMED_RESPONSE → GraderPermanentFailure."""
          calls = [0]
          def fn():
              calls[0] += 1
              raise Exception("json decode error parsing response")
          policy = RetryPolicy(max_attempts=3, overall_deadline=10.0)
          observer = GradingObserver(log_dir=tmp_path)
          try:
              call_with_retry(fn, policy=policy, observer=observer)
              assert False
          except GraderPermanentFailure as exc:
              assert exc.error_class == GraderErrorClass.MALFORMED_RESPONSE
          assert calls[0] == 1, "Must not retry MALFORMED_RESPONSE"
  ```
Next micro-step: TC-LGT-006-04
```

```
Child Taskcard ID: TC-LGT-006-04
Parent Taskcard ID: TC-LGT-006
Title: Add REL-024 — KeyboardInterrupt → CANCELLED permanent failure
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-006-04-01
```

```
Micro-step ID: MS-LGT-006-04-01
Child Taskcard ID: TC-LGT-006-04
Status: PENDING
Action: Append TestCancellation class:
  ```python
  class TestCancellation:
      def test_keyboard_interrupt_cancelled(self, tmp_path):
          """REL-024: KeyboardInterrupt during fn() → GraderPermanentFailure(CANCELLED)."""
          def fn():
              raise KeyboardInterrupt()
          policy = RetryPolicy(max_attempts=3, overall_deadline=10.0)
          observer = GradingObserver(log_dir=tmp_path)
          try:
              call_with_retry(fn, policy=policy, observer=observer)
              assert False
          except GraderPermanentFailure as exc:
              assert exc.error_class == GraderErrorClass.CANCELLED
  ```
Next micro-step: TC-LGT-006-05
```

```
Child Taskcard ID: TC-LGT-006-05
Parent Taskcard ID: TC-LGT-006
Title: Add REL-025 — GraderCircuitBreaker opens after 5 failures
Type: CHILD
Status: TODO

Preconditions:
  - TC-LGT-004 CLOSED (GraderCircuitBreaker must be importable)

Micro-steps:
  - MS-LGT-006-05-01
```

```
Micro-step ID: MS-LGT-006-05-01
Child Taskcard ID: TC-LGT-006-05
Status: PENDING
Action: Append TestGraderCircuitBreaker class:
  ```python
  class TestGraderCircuitBreaker:
      def test_opens_after_failure_threshold(self):
          """REL-025: 5 consecutive failures → circuit OPEN."""
          breaker = GraderCircuitBreaker(failure_threshold=5, reset_timeout=60.0)
          assert breaker.is_open() is False
          for _ in range(5):
              breaker.record_failure()
          assert breaker.is_open() is True

      def test_record_success_closes_circuit(self):
          """REL-025b: record_success after OPEN → CLOSED."""
          breaker = GraderCircuitBreaker(failure_threshold=2, reset_timeout=60.0)
          breaker.record_failure()
          breaker.record_failure()
          assert breaker.is_open() is True
          breaker.record_success()
          assert breaker.is_open() is False
  ```
Note: GraderCircuitBreaker must be imported at top of test file (add to import block)
Next micro-step: TC-LGT-006-06
```

```
Child Taskcard ID: TC-LGT-006-06
Parent Taskcard ID: TC-LGT-006
Title: Add REL-026 — circuit HALF_OPEN probe success closes circuit
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-006-06-01
```

```
Micro-step ID: MS-LGT-006-06-01
Child Taskcard ID: TC-LGT-006-06
Status: PENDING
Action: Append to TestGraderCircuitBreaker class:
  ```python
      def test_half_open_after_reset_timeout(self):
          """REL-026: After reset_timeout, circuit allows one probe (HALF_OPEN)."""
          import grader_reliability as _gr
          breaker = GraderCircuitBreaker(failure_threshold=1, reset_timeout=30.0)
          breaker.record_failure()
          assert breaker.is_open() is True
          # Simulate time passing beyond reset_timeout
          _time_ref = [0.0]
          def fake_mono():
              _time_ref[0] += 40.0
              return _time_ref[0]
          with patch("grader_reliability.time.monotonic", side_effect=fake_mono):
              # is_open() transitions to HALF_OPEN after timeout
              result = breaker.is_open()
          # In HALF_OPEN state, is_open() returns False (allow probe)
          assert result is False
          # Probe succeeds → CLOSED
          breaker.record_success()
          assert breaker.is_open() is False
  ```
Next micro-step: TC-LGT-006-07
```

```
Child Taskcard ID: TC-LGT-006-07
Parent Taskcard ID: TC-LGT-006
Title: Run all REL-001 to REL-026 and confirm all pass
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-006-07-01
  - MS-LGT-006-07-02
```

```
Micro-step ID: MS-LGT-006-07-01
Child Taskcard ID: TC-LGT-006-07
Status: PENDING
Action: Run .venv/Scripts/pytest tests/supervisor/test_grader_reliability.py -v 2>&1
Expected output: 26 tests passed; 0 failed; 0 errors
Failure handling: Fix only the failing test; re-run
Next micro-step: MS-LGT-006-07-02
```

```
Micro-step ID: MS-LGT-006-07-02
Child Taskcard ID: TC-LGT-006-07
Status: PENDING
Action: Capture final pytest output as evidence for TC-LGT-006 parent acceptance
Next micro-step: TC-LGT-007 (final parent)
```

---

```
Parent Taskcard ID: TC-LGT-007
Title: Create pilot_grader.py — 8 fault-injection proof pilots
Type: PARENT
Status: READY (depends on TC-LGT-004 CLOSED — circuit breaker needed for pilot 5)
Owner: reliability_agent
Priority: Low (plan outcome not blocked by TC-LGT-007; all other parents can close without it)

Source:
  Plan requirement ID: REQ-LGT-012
  Plan section: Implementation Plan TC-LGT-007

Objective:
  - Self-contained script proving 8 fault scenarios with no live network

Dependencies:
  - TC-LGT-001 CLOSED (GRADER_LOG_DIR for log isolation)
  - TC-LGT-004 CLOSED (GraderCircuitBreaker for pilot 5)

Child taskcards:
  - TC-LGT-007-01  (create tools/supervisor/pilots/ dir and pilot_grader.py)
  - TC-LGT-007-02  (pilot 1: normal grading)
  - TC-LGT-007-03  (pilot 2: SSL read timeout → retry → success)
  - TC-LGT-007-04  (pilot 3: 5xx + reset → retry)
  - TC-LGT-007-05  (pilot 4: auth failure → no retry)
  - TC-LGT-007-06  (pilot 5: circuit breaker opens → fast-fail)
  - TC-LGT-007-07  (pilot 6: restart → cache resume idempotency)
  - TC-LGT-007-08  (pilot 7: concurrent calls, shared breaker)
  - TC-LGT-007-09  (pilot 8: same input rerun → cache hit, 0 LLM calls)
  - TC-LGT-007-10  (run all pilots, verify all pass)

Parent acceptance criteria:
  - pilot_grader.py --all exits 0
  - Each pilot prints PASS
  - No live network calls required
```

```
Child Taskcard ID: TC-LGT-007-01
Parent Taskcard ID: TC-LGT-007
Title: Create tools/supervisor/pilots/ directory and empty pilot_grader.py scaffold
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-007-01-01
  - MS-LGT-007-01-02
```

```
Micro-step ID: MS-LGT-007-01-01
Child Taskcard ID: TC-LGT-007-01
Status: PENDING
Action: Verify tools/supervisor/pilots/ directory does not already exist
        If it does, confirm it does not contain a conflicting pilot_grader.py
Allowed operation: inspect (ls or Glob)
Next micro-step: MS-LGT-007-01-02
```

```
Micro-step ID: MS-LGT-007-01-02
Child Taskcard ID: TC-LGT-007-01
Status: PENDING
Action: Create tools/supervisor/pilots/pilot_grader.py with this scaffold:
  ```python
  """pilot_grader.py — 8 fault-injection pilots for grader reliability hardening.
  Usage: python tools/supervisor/pilots/pilot_grader.py --pilot N  (N=1..8)
         python tools/supervisor/pilots/pilot_grader.py --all
  All pilots use unittest.mock — no live network calls required.
  """
  from __future__ import annotations
  import argparse, sys, os, tempfile
  from pathlib import Path
  from unittest.mock import patch, MagicMock

  _REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
  sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
  os.environ.setdefault("GRADER_LOG_DIR", tempfile.mkdtemp())

  from grader_reliability import (
      RetryPolicy, GradingObserver, call_with_retry,
      GraderRetryExhausted, GraderPermanentFailure, GraderErrorClass,
      GraderCircuitBreaker,
  )

  _PILOTS: dict[int, tuple[str, callable]] = {}
  def pilot(n: int, name: str):
      def dec(fn):
          _PILOTS[n] = (name, fn)
          return fn
      return dec
  ```
Forbidden: Add any implementation code beyond the scaffold
Next micro-step: TC-LGT-007-02
```

```
Child Taskcard ID: TC-LGT-007-02 through TC-LGT-007-09
Parent Taskcard ID: TC-LGT-007
Title: Implement pilots 1 through 8 in pilot_grader.py
Type: CHILD (grouped for brevity; execute one pilot function per micro-step)
Status: TODO

Pilots to implement (append to pilot_grader.py sequentially):

Pilot 1 (normal): fn() returns "ok" → call_with_retry succeeds on first attempt; assert result == "ok"
Pilot 2 (SSL timeout): fn() raises ReadTimeout twice then returns "ok"; assert 3 calls made
Pilot 3 (5xx+reset): fn() raises PROVIDER_5XX once, CONNECTION_RESET once, then returns "ok"
Pilot 4 (auth): fn() raises AuthenticationError → GraderPermanentFailure(AUTHENTICATION_FAILURE); assert 1 call
Pilot 5 (circuit): GraderCircuitBreaker(failure_threshold=3); 3 failures → OPEN; 4th call raises CIRCUIT_OPEN immediately
Pilot 6 (cache resume): _cache_grade writes a result; call semantic_verify_item mock → returns cached without LLM call
Pilot 7 (concurrent): ThreadPoolExecutor(max_workers=5) runs 5 simultaneous call_with_retry calls; assert all complete
Pilot 8 (idempotent): Same item_id+ev_hash graded twice; second run returns _from_cache=True; provider not called

Each pilot function: uses patch(time.sleep), tmp_path observer, prints PASS/FAIL, returns bool
Add main() and if __name__=="__main__" block with argparse at the end.
```

```
Child Taskcard ID: TC-LGT-007-10
Parent Taskcard ID: TC-LGT-007
Title: Run all 8 pilots and confirm all pass
Type: CHILD
Status: TODO

Micro-steps:
  - MS-LGT-007-10-01
```

```
Micro-step ID: MS-LGT-007-10-01
Child Taskcard ID: TC-LGT-007-10
Status: PENDING
Action: python tools/supervisor/pilots/pilot_grader.py --all
Expected output: "Pilot 1 PASS" through "Pilot 8 PASS"; exit 0
Failure handling: Read FAIL output for specific pilot; fix only that pilot; re-run
```

---

## [SECTION F] EXECUTION DAG AND DEPENDENCY MODEL

```yaml
# artifact_role: execution_dag
# execution_authority: false
# authoritative_plan: warm-enchanting-grove.md

execution-dag:
  # Parent taskcard execution order (strict where sequential, parallel-safe where noted)

  TC-LGT-001:
    prerequisites: []
    children_sequential: [TC-LGT-001-01, TC-LGT-001-02, TC-LGT-001-03]
    note: Must close first; all other parents require TC-LGT-001-01 for GRADER_LOG_DIR

  TC-LGT-002:
    prerequisites: [TC-LGT-001-01]
    children_sequential: [TC-LGT-002-01, TC-LGT-002-02, TC-LGT-002-03, TC-LGT-002-04, TC-LGT-002-05]

  TC-LGT-003:
    prerequisites: [TC-LGT-001-01, TC-LGT-002]
    children_sequential: [TC-LGT-003-01, TC-LGT-003-02]
    note: TC-LGT-002 must be CLOSED first — establishes the pattern to replicate exactly

  TC-LGT-004:
    prerequisites: [TC-LGT-001-01]
    children_sequential: [TC-LGT-004-01, TC-LGT-004-02, TC-LGT-004-03, TC-LGT-004-04, TC-LGT-004-05]
    parallel_with: [TC-LGT-002, TC-LGT-005]  # no file overlap

  TC-LGT-005:
    prerequisites: [TC-LGT-001-01]
    children_sequential: [TC-LGT-005-01, TC-LGT-005-02, TC-LGT-005-03, TC-LGT-005-04]
    parallel_with: [TC-LGT-004]  # different files

  TC-LGT-006:
    prerequisites: [TC-LGT-001, TC-LGT-004]
    children_sequential: [TC-LGT-006-01 through TC-LGT-006-07]
    note: REL-025/026 require GraderCircuitBreaker from TC-LGT-004

  TC-LGT-007:
    prerequisites: [TC-LGT-001, TC-LGT-004]
    parallel_with: [TC-LGT-006]  # different file (pilots vs tests)

  critical_path: TC-LGT-001 → TC-LGT-002 → TC-LGT-004 → TC-LGT-006

file-ownership-and-locks:
  tools/supervisor/grader_reliability.py:
    owner: [TC-LGT-001-01, TC-LGT-004]
    lock_rule: TC-LGT-001-01 closes before TC-LGT-004 edits same file
    conflict_risk: MEDIUM — both edit the same file; sequence strictly

  tools/supervisor/grade_declared_work.py:
    owner: [TC-LGT-002, TC-LGT-005]
    conflict_risk: MEDIUM — both edit same file; sequence strictly
    lock_rule: TC-LGT-002 closes before TC-LGT-005 starts (different functions, but same file)

  tools/supervisor/adversarial_check.py:
    owner: [TC-LGT-003]
    conflict_risk: LOW

  tests/supervisor/test_grader_reliability.py:
    owner: [TC-LGT-001-02, TC-LGT-006]
    conflict_risk: HIGH — both edit same test file
    lock_rule: TC-LGT-001-02 MUST close before TC-LGT-006 starts

  tools/supervisor/pilots/pilot_grader.py:
    owner: [TC-LGT-007]
    conflict_risk: NONE (new file)

parallel-execution-safety-map:
  SAFE_PAIRS:
    - [TC-LGT-004, TC-LGT-005]  # different files: grader_reliability.py vs grade_declared_work.py
    - [TC-LGT-006, TC-LGT-007]  # different files: test file vs pilots file
  UNSAFE_PAIRS:
    - [TC-LGT-001-01, TC-LGT-004]  # same file: grader_reliability.py
    - [TC-LGT-001-02, TC-LGT-006]  # same file: test_grader_reliability.py
    - [TC-LGT-002, TC-LGT-005]    # same file: grade_declared_work.py
```

---

## [SECTION G] MACHINE STATE MODEL

```yaml
# artifact_role: taskcard_state_machine
# execution_authority: false

parent_taskcard_states:
  valid: [PROPOSED, READY, IN_PROGRESS, CHILDREN_IN_PROGRESS, INTEGRATION_PENDING, VERIFIED, SCORED, CLOSED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]

  valid_transitions:
    PROPOSED → READY: when all inputs identified and prerequisites are CLOSED
    READY → IN_PROGRESS: when first child starts
    IN_PROGRESS → CHILDREN_IN_PROGRESS: when all children are started
    CHILDREN_IN_PROGRESS → INTEGRATION_PENDING: when all mandatory children CLOSED
    INTEGRATION_PENDING → VERIFIED: when parent integration checks pass
    VERIFIED → SCORED: when quality dimensions scored
    SCORED → CLOSED: when all dimensions >= 4/5
    SCORED → REROUTED: when any dimension < 4/5
    any → BLOCKED: when hard dependency not met
    BLOCKED → READY: when dependency resolved
    any → BLOCKED_EXTERNAL: when True External Gate required
    any → DEFERRED_WITH_REASON: with documented reason

  invalid_transitions:
    READY → CLOSED: forbidden
    CHILDREN_IN_PROGRESS → CLOSED: forbidden (must go through INTEGRATION_PENDING)
    REROUTED → CLOSED: forbidden without rework and re-verification

child_taskcard_states:
  valid: [TODO, READY, IN_PROGRESS, IMPLEMENTED, VERIFIED, SCORED, CLOSED, REROUTED, BLOCKED, BLOCKED_EXTERNAL, DEFERRED_WITH_REASON]

  valid_transitions:
    TODO → READY: when parent is IN_PROGRESS and preconditions met
    READY → IN_PROGRESS: when first micro-step starts
    IN_PROGRESS → IMPLEMENTED: when all micro-steps COMPLETE
    IMPLEMENTED → VERIFIED: when acceptance checks pass
    VERIFIED → SCORED: when quality gates scored
    SCORED → CLOSED: when all required gates >= 4/5
    SCORED → REROUTED: when any required gate < 4/5
    REROUTED → IN_PROGRESS: after rework defined

  invalid_transitions:
    TODO → CLOSED: forbidden
    READY → CLOSED: forbidden
    IMPLEMENTED → CLOSED: forbidden (must verify first)
    REROUTED → CLOSED: forbidden without rework evidence

micro_step_states:
  valid: [PENDING, READY, ACTIVE, COMPLETE, FAILED, BLOCKED, SKIPPED_NOT_APPLICABLE]

  valid_transitions:
    PENDING → READY: when child is IN_PROGRESS
    READY → ACTIVE: when execution starts
    ACTIVE → COMPLETE: when expected output produced
    ACTIVE → FAILED: when expected output not produced
    ACTIVE → BLOCKED: when external dependency blocks
    FAILED → READY: after diagnosis and fix
    BLOCKED → READY: after dependency resolved
    PENDING → SKIPPED_NOT_APPLICABLE: with documented reason (e.g., "import already present")

  invalid_transitions:
    PENDING → COMPLETE: forbidden (must be ACTIVE first)
    COMPLETE → FAILED: forbidden (re-execute as new ACTIVE micro-step)

quality_scoring_thresholds:
  mandatory_minimum: 4/5
  below_threshold_action: REROUTED
  dimensions_child:
    - requirement_correctness
    - implementation_correctness
    - scope_discipline
    - validation_strength
    - evidence_completeness
    - regression_safety
  dimensions_parent:
    - root_cause_coverage
    - child_completeness
    - integration_completeness
    - dependency_correctness
    - evidence_completeness
```

---

## [SECTION H] VALIDATION MATRIX

```yaml
# artifact_role: verification_matrix
# execution_authority: false

validations:
  TC-LGT-001:
    integration:
      - check: "Import grader_reliability with GRADER_LOG_DIR=/tmp/x → GradingObserver() writes to /tmp/x/"
        method: python -c inline
        mandatory: true
      - check: "pytest tests/supervisor/test_grader_reliability.py leaves grader-events.jsonl unchanged"
        method: sha256 before/after
        mandatory: true
    regression:
      - check: "REL-001 to REL-020 all pass after TC-LGT-001 edits"
        command: .venv/Scripts/pytest tests/supervisor/test_grader_reliability.py -v
        mandatory: true

  TC-LGT-002:
    focused:
      - check: "grade_declared_work.py imports without error"
        command: python -c "import sys; sys.path.insert(0,'tools/supervisor'); import grade_declared_work"
      - check: "_sv_llm_call with gw raising → SDK fallback called"
        method: mock gw to raise; verify _sv_sdk_fallback invoked
        mandatory: true
      - check: "_sv_llm_call with gw returning empty → SDK fallback called"
        method: mock gw to return {"content":""}; verify _sv_sdk_fallback invoked
        mandatory: true
    negative_controls:
      - check: "_sv_sdk_fallback NOT called when gateway returns non-empty content"
        method: mock gw to return {"content":"ok"}; verify _sv_sdk_fallback NOT called
        mandatory: true

  TC-LGT-003:
    focused:
      - check: "run_adversarial_check with gw raising → returns {'status':'skipped'}"
        method: python -c inline mock
        mandatory: true
      - check: "Never raises from run_adversarial_check"
        method: all code paths verified to return dict
        mandatory: true

  TC-LGT-004:
    unit:
      - REL-025: 5 failures → is_open() True
      - REL-026: after reset_timeout → is_open() False (probe allowed)
      - record_success after OPEN → is_open() False
    integration:
      - check: "call_with_retry with OPEN breaker → GraderPermanentFailure(CIRCUIT_OPEN) on attempt 0"
        mandatory: true
      - check: "call_with_retry with circuit_breaker=None → identical behavior to current"
        mandatory: true
    regression:
      - REL-001 to REL-020 all pass with new circuit_breaker param (default None)

  TC-LGT-005:
    focused:
      - check: "Terminal fallback writes fail: cache entry"
        method: call semantic_verify_item with LLM unavailable; inspect cache file
        mandatory: true
      - check: "Immediate rerun returns _from_cache=True without calling LLM"
        method: two sequential calls with LLM mocked to track calls
        mandatory: true
      - check: "max_age_minutes=30 expires after 30+ min (fake clock)"
        method: fake datetime to advance by 35 min; confirm cache miss
        mandatory: false  # nice-to-have

  TC-LGT-006:
    unit:
      - All REL-021 through REL-026 pass
    regression:
      - All REL-001 through REL-020 still pass

  TC-LGT-007:
    pilots:
      - pilot_grader.py --all → exit 0
      - All 8 pilots print PASS

negative_controls:
  NC-001: "GradingObserver writes to GRADER_LOG_DIR when set, not to .local/"
  NC-002: "SDK fallback NOT invoked when gateway succeeds"
  NC-003: "AUTHENTICATION_FAILURE not retried (even with circuit breaker CLOSED)"
  NC-004: "Circuit breaker OPEN does not retry — immediate GraderPermanentFailure"
  NC-005: "Failure sentinel not returned after 30-min TTL expires"
  NC-006: "Parent taskcard cannot close with any child in non-CLOSED state"
```

---

## [SECTION I] EVIDENCE CONTRACT

```yaml
# artifact_role: evidence_contract
# execution_authority: false

evidence_root: .local/evidences/llm-grader-timeout-hardening/

evidence_obligations:
  TC-LGT-001:
    - sha256_before: SHA-256 of grader-events.jsonl before test run
    - sha256_after: SHA-256 of grader-events.jsonl after test run
    - pytest_output: full -v output of REL-001 to REL-020
    - diff: diff of grader_reliability.py changes

  TC-LGT-002:
    - diff: diff of _sv_llm_call changes in grade_declared_work.py
    - syntax_check: python import check output
    - mock_test_output: result of inline mock test for gateway→SDK fallback
    - regression: pytest REL-001 to REL-020 pass

  TC-LGT-003:
    - diff: diff of adversarial_check.py changes
    - non_blocking_proof: output of non-blocking test

  TC-LGT-004:
    - diff: diff of grader_reliability.py circuit breaker additions
    - unit_test_output: REL-025 and REL-026 pass
    - backward_compat: REL-001 to REL-020 still pass

  TC-LGT-005:
    - diff: diff of grade_declared_work.py failure sentinel changes
    - inline_test_output: PASS from MS-LGT-005-04-01 inline test

  TC-LGT-006:
    - final_pytest_output: all 26 REL tests pass

  TC-LGT-007:
    - pilot_output: pilot_grader.py --all exit 0 with PASS lines

incident_record:
  path: .local/incidents/llm-grader-timeout-001.yaml
  to_be_created_during: TC-LGT-001 execution
  content:
    incident_id: LLM-GRADER-TIMEOUT-001
    root_cause: test_artifacts_in_production_log + gateway_path_no_retry
    timeout_before: read=30s, connect=10s, 3 attempts, 95s deadline
    timeout_after: same for SDK; gateway adds max_attempts=2, deadline=45s
    evidence: .local/evidences/llm-grader-timeout-hardening/
    verdict: HEALED_AND_PILOT_PROVEN (pending TC-LGT-007)
```

---

## [SECTION J] TRACEABILITY ARTIFACTS

```yaml
# artifact_role: end_to_end_traceability
# execution_authority: false

traceability:
  REQ-LGT-001 → TC-LGT-001 → TC-LGT-001-01 → MS-LGT-001-01-[01..05]
  REQ-LGT-002 → TC-LGT-001 → TC-LGT-001-02 → MS-LGT-001-02-[01..04]
  REQ-LGT-003 → TC-LGT-002 → TC-LGT-002-[01..05] → MS-LGT-002-*
  REQ-LGT-004 → TC-LGT-002 → TC-LGT-002-04 → MS-LGT-002-04-01
  REQ-LGT-005 → TC-LGT-003 → TC-LGT-003-[01..02] → MS-LGT-003-*
  REQ-LGT-006 → TC-LGT-004 → TC-LGT-004-01 → MS-LGT-004-01-[01..02]
  REQ-LGT-007 → TC-LGT-004 → TC-LGT-004-02 → MS-LGT-004-02-[01..02]
  REQ-LGT-008 → TC-LGT-004 → TC-LGT-004-03 → MS-LGT-004-03-[01..02]
  REQ-LGT-009 → TC-LGT-005 → TC-LGT-005-01 → MS-LGT-005-01-[01..02]
  REQ-LGT-010 → TC-LGT-005 → TC-LGT-005-[02..04] → MS-LGT-005-*
  REQ-LGT-011 → TC-LGT-006 → TC-LGT-006-[01..07] → MS-LGT-006-*
  REQ-LGT-012 → TC-LGT-007 → TC-LGT-007-[01..10] → MS-LGT-007-*

section-to-requirement-map:
  B.3 RC-1 → REQ-LGT-001, REQ-LGT-002
  B.3 RC-2 → REQ-LGT-003, REQ-LGT-005
  B.3 RC-3 → REQ-LGT-006, REQ-LGT-007, REQ-LGT-008
  B.3 RC-4 → REQ-LGT-009, REQ-LGT-010
  B.3 RC-5 → REQ-LGT-004
  Implementation-Plan → REQ-LGT-011, REQ-LGT-012

stable-id-map:
  plan_domain: LGT  (LLM Grader Timeout)
  parent_ids: TC-LGT-001 through TC-LGT-007
  child_ids: TC-LGT-NNN-NN (two-digit child suffix)
  micro_step_ids: MS-LGT-NNN-NN-NN (two-digit child + two-digit step)
  requirement_ids: REQ-LGT-001 through REQ-LGT-012
  ID_stability: IDs derived from domain + objective order; stable across reruns
  regeneration_rule: Do not regenerate IDs on rerun; extend sequence if new items added
```

---

## [SECTION K] PLAN RECONCILIATION

```yaml
# artifact_role: plan_reconciliation_report
# execution_authority: false

sections_analyzed:
  - B.1 Context: PRESERVED intact
  - B.2 Already correct: PRESERVED intact
  - B.3 RC-1 through RC-5: PRESERVED intact; taskcards added
  - B.4 Out of Scope: PRESERVED intact
  - B.5 Tradeoffs: PRESERVED intact
  - B.6 Confidence: PRESERVED intact
  - C Requirements: NEW (12 requirements)
  - D Solution Options: NEW (4 problem areas evaluated)
  - E Execution Control: NEW (7 parents, 25+ children, 50+ micro-steps)
  - F DAG: NEW
  - G Machine State: NEW
  - H Validation Matrix: NEW
  - I Evidence Contract: NEW
  - J Traceability: NEW
  - K This section: NEW
  - L Execution Handoff: NEW

no-actionable-item-loss-audit:
  v1_TC-LGT-001: decomposed into 3 children, 9 micro-steps — COMPLETE
  v1_TC-LGT-002: decomposed into 5 children, 8 micro-steps — COMPLETE
  v1_TC-LGT-003: decomposed into 2 children, 3 micro-steps — COMPLETE
  v1_TC-LGT-004: decomposed into 5 children, 6 micro-steps — COMPLETE
  v1_TC-LGT-005: decomposed into 4 children, 5 micro-steps — COMPLETE
  v1_TC-LGT-006: decomposed into 7 children (one per REL test), 7 micro-steps — COMPLETE
  v1_TC-LGT-007: decomposed into 10 children — COMPLETE
  Verification steps (6 prose): converted to validation matrix entries — COMPLETE
  Tradeoffs: preserved in B.5 and surfaced in parent taskcard tradeoff notes — COMPLETE

single-plan-authority-audit:
  authoritative_plans_count: 1
  competing_plans: none
  supporting_artifacts: embedded within this file; non-authoritative; no execution instructions
  verdict: SINGLE_PLAN_AUTHORITY_CONFIRMED

contradiction-and-duplication-ledger:
  contradictions: none found
  duplicates: none (each requirement maps to exactly one parent; no TC overlaps)
  stale_content: v1 TC-LGT-001..007 prose retained but now superseded by parent taskcards in Section E
    action: prose sections renamed to "Historical context — see Section E for execution control"

idempotency-check:
  stable_ids: yes — TC-LGT-NNN IDs are sequence-derived; safe to rerun
  duplicate_detection: no duplicate parent IDs found
  rerun_rule: On rerun, skip CLOSED taskcards; re-execute only non-CLOSED children
```

---

## [SECTION L] EXECUTION HANDOFF

```yaml
# artifact_role: execution_handoff
# execution_authority: false
# authoritative_plan: C:\Users\prora\.claude\plans\warm-enchanting-grove.md

execution-readiness-verdict:
  ready: true
  next_parent: TC-LGT-001
  next_child: TC-LGT-001-01
  first_micro_step: MS-LGT-001-01-01
  blockers: none
  deferred: TC-LGT-007 (low priority; plan outcome not blocked)
```

### Execution Agent Instructions (mandatory — read before starting)

1. **Read this entire plan** before taking any action.

2. **Start with TC-LGT-001** (not any other taskcard). It is the only taskcard with no
   prerequisites. All others depend on TC-LGT-001-01 being CLOSED.

3. **Execute one micro-step at a time**. Do not batch micro-steps. Do not skip.
   For each micro-step:
   - Confirm its parent child taskcard ID
   - Confirm its preconditions are met
   - Execute exactly the specified `Action`
   - Capture the expected output
   - Mark micro-step COMPLETE before proceeding to next

4. **File ownership is strict** (see Section F). Do not touch files not listed in the
   current child taskcard's Allowed files.

5. **Do not close a child taskcard** until all its micro-steps are COMPLETE and all
   Acceptance checks pass.

6. **Do not close a parent taskcard** until all mandatory children are CLOSED and parent
   integration checks pass.

7. **Evidence is mandatory**. Every child taskcard requires at least one evidence item
   (diff, test output, or inline test result). Do not close without evidence.

8. **If a micro-step fails**: mark it FAILED, read the failure output, fix only the
   affected code, re-mark READY, re-execute. Do not skip.

9. **Reroute rule**: Any child quality gate below 4/5 → mark child REROUTED → create
   a repair micro-step → re-execute → re-score. Do not close a REROUTED child.

10. **After all 7 parent taskcards are CLOSED**: confirm all 26 REL tests pass; confirm
    pilot_grader.py --all exits 0; record final verdict as
    `LLM_GRADER_TIMEOUT_HEALED_AND_PILOT_PROVEN`.

### What the execution agent must NOT do

- Start TC-LGT-002 before TC-LGT-001-01 is CLOSED
- Start TC-LGT-005 before TC-LGT-002 is CLOSED (same file: grade_declared_work.py)
- Start TC-LGT-006 before TC-LGT-001-02 is CLOSED (same file: test file)
- Start TC-LGT-006 REL-025/026 before TC-LGT-004 is CLOSED
- Treat a passing import check as sufficient evidence (also need test output)
- Treat code existence as validation (run the tests)
- Close parent while any mandatory child is not CLOSED
- Modify files not in the current child taskcard's Allowed files list
- Choose unrelated work from next-sprint.md (this plan is the sole authority)

---

## Audit Taskcard Status (lifecycle_audit.py format)

| TC-ID | Status |
|---|---|
| TC-LGT-001 | CLOSED |
| TC-LGT-002 | CLOSED |
| TC-LGT-003 | CLOSED |
| TC-LGT-004 | CLOSED |
| TC-LGT-005 | CLOSED |
| TC-LGT-006 | CLOSED |
| TC-LGT-007 | CLOSED |

---

## FINAL VERDICT

```
PLAN_MICRO_TASKCARDIZED_READY_FOR_EXECUTION

Active Plan: C:\Users\prora\.claude\plans\warm-enchanting-grove.md
Authority Source: explicit plan mode attachment
Duplicate Plans: none
Supporting Artifacts: embedded in this file; execution_authority=false

Decomposition:
  Parent taskcards: 7 (TC-LGT-001 through TC-LGT-007)
  Child taskcards: 27
  Micro-steps: 52
  Broad taskcards split: 7 (all v1 prose taskcards decomposed)

Traceability:
  All actionables mapped: yes
  All children linked to parents: yes
  All micro-steps linked to children: yes
  All validations linked: yes
  All evidence obligations linked: yes

Execution Readiness:
  Ready: yes
  Blockers: none
  First action: MS-LGT-001-01-01 (read grader_reliability.py lines 280-290)
  Plan outcome target: LLM_GRADER_TIMEOUT_HEALED_AND_PILOT_PROVEN
```


<!--plan_terminal_lock:
  status: TERMINAL_CLOSED
  locked_at: "2026-07-13T14:08:35.160401+00:00"
  locked_by: "c0d42e113626"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
