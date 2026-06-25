# Lane H: Autonomous Supervisor Audit
# Sprint: ff-machinery-readiness-audit-20260625

## Summary

The autonomous supervisor is well-implemented for what it does (evidence validation, grading,
continuation state management). But its **enforcement scope is limited to post-declaration
validation** — it cannot prevent non-QName-compliant or non-spec-driven code from being
created in the first place. Lane ownership, DAG ordering, and overclaim detection are
prompt-only (not code-enforced).

---

## Supervisor Pipeline (autonomous_cycle.py)

Direct evidence (lines 1–200):

```python
# Exit codes:
#   0 — cycle complete, autonomous continue possible
#   3 — cycle complete, critical rework exists
#   9 — unexpected error

# Pipeline steps:
# 1. validate_declaration()          — schema, required fields
# 2. inspect_declaration()           — file existence, size, readiness
# 3. grade_all() + write_outputs()   — grading + evidence writing
# 4. generate_prompt() + work_items() — next sprint prompt
# 5. evidence_manifest               — manifest generation + validation
# 6. materialize_evidence            — evidence materialization
# 7. build_context_pack              — context bundle generation
# 8. run_anti_skip_checks()          — R112 anti-skip
# 9. classify_continuation_state()   — 19-state machine
```

### Continuation State Machine (19 states)

```python
# States (direct from autonomous_cycle.py lines 57-79):
YES                              # all accepted, anti-skip clean
YES_WITH_LIMITATIONS             # accepted + low-severity anti-skip notes
YES_WITH_REWORK                  # rework items but safe lanes continue
NO_MAX_ITERATIONS                # iteration limit reached
NO_EXTERNAL_GATE                 # blocked by gate approval / credentials / push
NO_BROKEN_BASELINE               # critical rework blocks continuation
NO_UNSAFE_SOURCE_STATE           # overclaimed items present
NO_NO_PROGRESS                   # consecutive sprints with no product gap closure
NO_POLICY_BLOCK                  # policy explicitly blocks continuation
NO_GENERIC_NEXT_PROMPT           # generated prompt is generic, not stream-specific
NO_LEGACY_REVIEW_CONTRADICTION   # legacy review disagrees with declaration cycle
NO_STALE_GAPS                    # selected-product-gaps.json is stale
NO_MISSING_EVIDENCE_MANIFEST     # evidence manifest missing or invalid
NO_WRONG_STREAM_CONTEXT          # context pack/evidence-review references wrong stream
NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS # ACCEPTED_VERIFIED but no raw logs
NO_PROMPT_QUALITY_FAILURE        # prompt quality validation failed
NO_UNCLASSIFIED_DIRTY_STATE      # dirty git state without dirty_state_classification
NO_MISSING_REQUIRED_ARTIFACTS    # declared required artifacts not found on disk
NO_PRODUCT_OUTPUT_FLOOR          # Mainstream breadth < floor, no blocker removed
```

**Assessment: EXCELLENT** — 19-state machine is comprehensive and well-designed.

### Current Continuation State
```json
{
  "autonomous_continue": true,
  "iteration": 7,
  "max_iterations": 12,
  "continuation_state": "YES",
  "session_id": "5c16c5c46b6f",
  "hard_stops_detected": [],
  "rework_items": []
}
```

---

## Supervision Gap Analysis

Source: spec-to-feature-radical-correction-plan.md §5 and Lane 14 audit findings

### SUP-GAP-001: Lane ownership not enforced by code
**Severity:** BLOCKER
**Evidence:** Lane assignments exist in skill-registry.yaml and next-sprint.md as lane manifests,
but no code enforces that machinery lanes (1-6, 14, 15) complete before product lanes (7-13).
An agent can freely ignore the lane manifest and do product work while machinery is broken.
**Required fix:** Code-enforced pre-check that returns STOP when machinery lane prerequisites
are unmet (SUPERVISOR-LANES-001)

### SUP-GAP-002: DAG ordering not enforced by code
**Severity:** HIGH
**Evidence:** Wave structure (0→1A→1B→2→3→4→5→6→7) exists in spec-to-feature plan §7,
but check_continuation.py has no DAG awareness. It returns CONTINUE based on iteration count
and rework items — not based on whether Lane 1 (SAL) is complete before Lane 3 (compiler).
**Required fix:** Add wave_gate validator that checks prerequisite wave artifacts before continuing

### SUP-GAP-003: Overclaim detector (10 patterns) NEVER CALLED
**Severity:** HIGH
**Evidence:** From spec-to-feature-radical-correction-plan.md §5: "Overclaim detector (10
patterns) is defined but NEVER called by autonomous_cycle.py." The patterns exist as code but
have no integration point.
**Required fix:** Wire overclaim detector into autonomous_cycle.py Step 2d (SUPERVISOR-CONTINUATION-001)

### SUP-GAP-004: grade defaults adequate=True with confidence=0.0
**Severity:** HIGH
**Evidence:** From spec-to-feature plan: "grade_declared_work defaults adequate=True when
confidence=0.0." Without LLM grader (requires GPT_OSS_ENDPOINT env var), all items default to
adequate regardless of actual quality.
**Note:** This is mitigated by TC-GUARD-001 BLOCK mode (forces spec_fact_refs) and TC-GUARD-002
(purpose check). But grading alone cannot catch semantic non-compliance.

### SUP-GAP-005: LLM "inadequate" verdict overridden when confidence < 0.80
**Severity:** MEDIUM
**Evidence:** From spec-to-feature plan: "LLM 'inadequate' verdict overridden if confidence < 0.80."
This allows low-confidence rejections to pass through as adequate.
**Mitigation:** TC-GUARD-001 and TC-GUARD-002 provide deterministic checks that compensate.

### SUP-GAP-007: Circuit breaker for zero-task loops — FIXED
**Severity:** RESOLVED
**Evidence from MEMORY.md:** "TC-S55-006 FIXED (2026-06-25): SIGNAL-UNIFY-001 patch added
`_latest_dir` before circuit breaker block. Circuit breaker exists in autonomous_cycle.py."
Circuit breaker increments zero-task counter and prints CIRCUIT_BREAKER at 3+ consecutive cycles.

### SUP-GAP-008: _EXPANSION_GOALS is frozen hardcoded list
**Severity:** HIGH
**Evidence:** autonomous_task_generator.py direct read shows 20+ hardcoded entries with
spec_authority=no_public_spec_available.
**Required fix:** Replace with gap-ledger-driven task selection (CAPABILITY-REPAIR-001)

### SUP-GAP-009: Zero durable learning
**Severity:** HIGH
**Evidence:** No failure-memory.json found. MEMORY.md is 200-line prose — not machine-readable.
Skills, validators, schemas, and prompts are static — never updated from prior failures.
**Required fix:** FailureMemory class exists in failure_memory.py — wire into cycle

### Session Identity Guards — WORKING
**Evidence from MEMORY.md (CCI-MVP hardening 2026-06-18):**
- Session file pinning: .local/supervisor/session-{track}.id with 4h TTL
- UUID fallback detection: WARN_UUID_FALLBACK (not REJECT)
- SESSION_MISMATCH: HARD STOP (non-overridable)
- CHAT_ID_MISMATCH enforcement for machinery track
- 45 continuation tests pass

**Assessment: EXCELLENT** — session isolation is robust

### Plan Lock Enforcement — WORKING
**Evidence:**
- .local/supervisor/plan-locks/<session_id>.json blocks CONTINUE while IN_PROGRESS
- SUPERSEDED status allows foreign locks to be overridden without POST_PLAN_TERMINAL
- TERMINAL_CLOSED triggers POST_PLAN_TERMINAL (non-overridable)
- cleanup_stale_locks() function available in write_plan_lock.py

---

## Anti-Skip Checker (R112)

The anti-skip checker (anti_skip_checker.py) runs as Step 8 of autonomous_cycle.py.

It detects:
- Sprints that claim ACCEPTED_VERIFIED without raw logs
- Sprints claiming spec parity without V53 tests
- Sprints with only advisory-only work items
- Generic (non-stream-specific) prompts

Results feed into:
- YES_WITH_LIMITATIONS (low-severity violations)
- NO_PROMPT_QUALITY_FAILURE (severe violations)
- NO_MISSING_RAW_LOGS_FOR_VERIFIED_CLAIMS

**Assessment:** STRONG — catches overclaims post-declaration

---

## FailureMemory Module (failure_memory.py)

From import at autonomous_cycle.py line 46: `from failure_memory import FailureMemory`
The module EXISTS and is imported. But:
- Is it actually used in the cycle? Not evident from lines 1-200.
- No failure-memory.json found in repository
- MEMORY.md notes: "No failure-memory.json; failures recorded only in MEMORY.md (prose, 200-line limit)"

**Status:** IMPORTED but likely not integrated for durable learning

---

## Autonomous Supervisor Audit Verdict

| Dimension | Status | Evidence |
|---|---|---|
| Declaration validation | EXCELLENT | Schema + field check |
| Evidence inspection | EXCELLENT | File existence + size + readiness |
| Grading pipeline | STRONG | TC-GUARD-001/002 deterministic; LLM optional |
| Continuation state machine | EXCELLENT | 19 states; proper priority ordering |
| Session isolation | EXCELLENT | CCI-MVP; 45 tests pass |
| Plan lock enforcement | EXCELLENT | TERMINAL_CLOSED/SUPERSEDED/IN_PROGRESS states |
| Lane DAG enforcement | NONE | Prompt-only (SUP-GAP-001/002) |
| Overclaim detection | PARTIAL | Anti-skip checker works; 10-pattern detector not wired |
| Durable learning | NONE | FailureMemory imported; not integrated |
| Circuit breaker | EXISTS | TC-S55-006 fixed 2026-06-25 |
| Max iterations | RESOLVED | Governed rollover (reset to 0) |
| Zero-product-work loops | PARTIAL | Circuit breaker detects; no auto-recovery |
