# velvet-swinging-wreath — Machinery Iteration Failure & Lifecycle Healing Plan

**plan_type:** machinery_hardening
**mission_id:** VELVET-SWINGING-WREATH-001
**created:** 2026-07-10
**status:** IN_PROGRESS
**authority:** This file is the SOLE work-selection authority for this conversation.
**in_repo_path:** plans/.claude/velvet-swinging-wreath.md

---

## § STEP 0 — MANDATORY PLAN MIGRATION (execute first, before all taskcards)

This plan file was seeded at an external path (`C:\Users\prora\.claude\plans\velvet-swinging-wreath.md`).
Before running any taskcard, the execution agent MUST:

```bash
# 1. Copy to in-repo location
cp "C:/Users/prora/.claude/plans/velvet-swinging-wreath.md" \
   "plans/.claude/velvet-swinging-wreath.md"

# 2. Write the plan lock to the IN-REPO path
python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/velvet-swinging-wreath.md

# 3. All subsequent reads, writes, taskcard updates, and audit calls use in-repo path
```

After migration, the external file is a SEED ONLY — never write to it again.

---

## Context

### What failed

Machinery plans (e.g., `vast-weaving-lampson.md`, `gov-window-fix-001.md`) execute one pass
of taskcards and stop. The required repeated lifecycle:

```
AUDIT → GAP ANALYSIS → PLAN HARDENING → EXECUTE → VERIFY → RE-AUDIT → REPEAT
```

...does not fire. After all current taskcards reach CLOSED, `lifecycle_audit.py` returns AUDIT_PASS,
`write_plan_lock.py --terminal --audit-gate` writes TERMINAL_CLOSED, and `check_continuation.py`
returns POST_PLAN_TERMINAL — a hard session stop. The mission terminates after one execution pass
without behavioral proof that the lifecycle loop was exercised across 2+ cycles.

### Root Cause Summary (from codebase forensics — pre-plan exploration + code inspection)

Six root causes work together to produce the one-pass termination failure:

| RC-ID | Root Cause | Component | Severity |
|-------|-----------|-----------|----------|
| RC-001 | `lifecycle_audit.py` AUDIT_PASS never reads mission-ledger iteration state | `lifecycle_audit.py` | CRITICAL |
| RC-002 | Each new machinery plan gets no fresh mission-ledger entry; old entry is reused | `write_plan_lock.py` init | HIGH |
| RC-003 | G3/G4 guards are MEDIUM warnings only — non-blocking; G4 skips when audit log absent | `lifecycle_audit.py` G4 | HIGH |
| RC-004 | No automatic taskcard generation when ITERATION_REQUIRED fires | `lifecycle_audit.py` / `write_plan_lock.py` | HIGH |
| RC-005 | check_continuation Check 1c returns STOP "MACHINERY_AUDIT_REQUIRED" — agent needs explicit routing instruction | `check_continuation.py` | MEDIUM |
| RC-006 | No V_MACH_* governance validators enforce behavioral iteration minimum | `governance_validators_ext4.py` | MEDIUM |

### What must be repaired

1. **RC-001 fix:** Add Check B1 to `lifecycle_audit.py`: for machinery_hardening plans, require `current_behavioral_iterations >= 2` from mission-ledger.json before AUDIT_PASS.
2. **RC-002 fix:** Add mission-ledger initialization in `write_plan_lock.py` for new machinery missions.
3. **RC-003 fix:** Escalate G4 to CRITICAL when `sprint-audit-log.json` is completely absent (audit never ran, not just stale).
4. **RC-004 fix:** Add `generate_behavioral_gap_taskcards(findings, plan_path)` — auto-appends new taskcards to plan file on ITERATION_REQUIRED.
5. **RC-005 fix:** Add explicit routing comment to check_continuation output when MACHINERY_AUDIT_REQUIRED fires, directing agent to run `lifecycle_audit.py`.
6. **RC-006 fix:** Add 4 V_MACH_* validators to `governance_validators_ext4.py`; update expected_count 167 → 171.

---

## Governing Architecture

### What already works (PRESERVE — do not redesign these)

| Component | Path | What it does | Status |
|-----------|------|-------------|--------|
| lifecycle_audit.py | `tools/supervisor/lifecycle_audit.py` | 4 guards (G1/G2 CRITICAL, G3/G4 MEDIUM), AUDIT_PASS/ITERATION_REQUIRED logic | EXISTS, WORKING |
| write_plan_lock.py | `tools/supervisor/write_plan_lock.py` | --audit-gate auto-calls lifecycle_audit, routes to TERMINAL_CLOSED or ITERATION_REQUIRED | EXISTS, WORKING |
| check_continuation.py | `tools/supervisor/check_continuation.py` | Check 1b (plan lock), Check 1c (mission-ledger), 10-check gate | EXISTS, WORKING |
| mission-ledger.json | `.local/supervisor/machinery/mission-ledger.json` | Full machinery mission state schema (audit_pending, current_iteration, stop_status...) | EXISTS, has stale mission entry |
| pilots dir | `tests/supervisor/pilots/` | Directory + `__init__.py` + 1 pilot file | EXISTS, partial |
| autonomous_cycle.py | `tools/supervisor/autonomous_cycle.py` | machinery track routing, signal writes | EXISTS, WORKING |
| G1/G2 guards | `lifecycle_audit.py` lines 205-305 | Queue exhaustion + closeout-as-terminal blocking | EXISTS, CRITICAL severity |

### What must be redesigned (targeted surgical changes only)

| Item | Gap | Fix approach |
|------|-----|-------------|
| lifecycle_audit.py AUDIT_PASS | Does not check mission-ledger `current_behavioral_iterations` | Add Check B1 (new function) |
| lifecycle_audit.py G4 | Gracefully skips when sprint-audit-log.json absent (non-blocking) | Escalate to CRITICAL on absent (not just stale) |
| write_plan_lock.py | No per-mission mission-ledger initialization | Add `_init_machinery_mission_ledger(mission_id, plan_path)` |
| lifecycle_audit.py | No auto-taskcard generation on ITERATION_REQUIRED | Add `generate_behavioral_gap_taskcards(findings, plan_path)` |
| check_continuation.py | MACHINERY_AUDIT_REQUIRED stop has no routing instruction | Add `next_action` field to stop output JSON |
| governance_validators_ext4.py | No V_MACH_* validators | Add V_MACH_AUDIT_AFTER_EXEC, V_MACH_ITERATION_PROOF, V_MACH_CONTINUATION_CONSUMED, V_MACH_TASK_VS_MISSION |

---

## Authoritative File Paths

| Component | Path |
|-----------|------|
| Lifecycle audit | `tools/supervisor/lifecycle_audit.py` |
| Plan lock writer | `tools/supervisor/write_plan_lock.py` |
| Continuation checker | `tools/supervisor/check_continuation.py` |
| Autonomous cycle | `tools/supervisor/autonomous_cycle.py` |
| Mission ledger (machinery) | `.local/supervisor/machinery/mission-ledger.json` |
| Lifecycle audit results | `.local/supervisor/lifecycle-audit-results.json` |
| Governance validators ext4 | `tools/supervisor/governance_validators_ext4.py` |
| Governance validator runner | `tools/supervisor/governance_validator_runner.py` |
| Policies | `.supervisor/policies.yaml` |
| Plan locks dir | `.local/supervisor/plan-locks/` |
| Evidence root | `.local/evidences/` |
| Pilots dir | `tests/supervisor/pilots/` |
| This plan (in-repo) | `plans/.claude/velvet-swinging-wreath.md` |
| Artifacts dir | `plans/.claude/velvet-swinging-wreath-artifacts/` |

---

## § PRE-FILLED: Failed-Run Forensics

_Filled during pre-plan codebase exploration. Source: lifecycle-audit-results.json, plan locks, codebase read._

### Last machinery plan: vast-weaving-lampson.md (VWL-001)

**Timeline reconstruction:**

```yaml
lifecycle_event:
  - sequence: 1
    timestamp: "2026-07-10T09:28:16"
    stage: EXECUTION
    actor: execution_agent (session 033f6a1ae2f3)
    action: Executed TC-VWL-001 through TC-VWL-CLOSE (5 taskcards — fix V105/V106 detection windows)
    state_after: all_taskcards=CLOSED

  - sequence: 2
    timestamp: "2026-07-10T09:28:16"
    stage: LIFECYCLE_AUDIT
    actor: write_plan_lock.py --terminal --audit-gate
    action: Called lifecycle_audit.py with plan vast-weaving-lampson.md
    audit_input:
      open_taskcards: []
      open_gaps: []
      guard_results: []
    audit_output:
      verdict: AUDIT_PASS
      mission_complete: true
      next_iteration_required: false
      recommended_action: MISSION_COMPLETE
    state_after: AUDIT_PASS

  - sequence: 3
    timestamp: "2026-07-10T09:28:16"
    stage: PLAN_LOCK
    actor: write_plan_lock.py
    action: Wrote TERMINAL_CLOSED to plan lock
    state_after: status=TERMINAL_CLOSED

  - sequence: 4
    timestamp: next_check
    stage: CONTINUATION_CHECK
    actor: check_continuation.py
    action: Read TERMINAL_CLOSED lock → returned STOP(POST_PLAN_TERMINAL)
    state_after: SESSION_TERMINATED

  - sequence: MISSING
    stage: POST_EXECUTION_AUDIT
    expected_action: "Run re-audit to verify lifecycle machinery works across 2+ cycles"
    actual_action: "NOT PERFORMED — AUDIT_PASS was returned based on taskcard closure alone"
    divergence: FIRST_FAILING_BOUNDARY
```

### First divergence point

**Boundary:** `taskcards completed → post-execution behavioral audit`
**Status:** PRODUCER_ONLY (taskcards CLOSED, but no behavioral iteration check)
**Root cause:** lifecycle_audit.py AUDIT_PASS condition checks current-moment state (open tasks=0, gaps=0)
but NEVER checks `mission-ledger.current_behavioral_iterations`. With 5 VWL taskcards closed and no
active gaps in the gap ledger, AUDIT_PASS fires immediately — even though VWL never ran a second
audit-execute-reaudit cycle.

### Confirmed: behavioral_iterations field does NOT exist

```bash
# grep confirmed: no "behavioral_iterations", "multi_iteration", "iteration_count" in lifecycle_audit.py
# Grep result: 0 matches
```

### Confirmed: mission-ledger.json exists but contains OLD mission

```json
{
  "mission_id": "machinery-lifecycle-healing-20260621",
  "current_iteration": 3,
  "stop_status": "MISSION_COMPLETE"
}
```

VWL-001 never wrote a NEW entry to mission-ledger.json. No VWL-001 mission_id entry exists.
The old entry (from June 2021) is stale and unrelated to VWL.

---

## § PRE-FILLED: Producer-Consumer Boundary Table

_Filled during pre-plan codebase exploration. Classifications based on actual code inspection._

| Boundary | Producer | Consumer | Status | Notes |
|----------|---------|---------|--------|-------|
| execution result → sprint audit | execution agent | lifecycle_audit.py (via --audit-gate) | CONNECTED_BUT_OPTIONAL | Only fires when agent explicitly calls write_plan_lock --audit-gate |
| sprint audit → gap register | lifecycle_audit.py | gap-ledger (implicit) | PRODUCER_ONLY | lifecycle_audit reads gap-ledger but does NOT update it |
| gap register → plan update | gap-ledger | agent (manual) | PRODUCER_ONLY | No automated plan update from gap register |
| plan update → plan hardening | plan file | agent (manual) | PRODUCER_ONLY | No automated plan hardening call |
| hardened plan → taskcard generation | plan file | agent (manual) | CONSUMER_MISSING | No auto-taskcard generation when ITERATION_REQUIRED fires |
| taskcards completed → post-execution audit | plan taskcards | lifecycle_audit.py | PRODUCER_ONLY | AUDIT_PASS fires on task closure alone; behavioral proof absent |
| audit result → mission ledger update | lifecycle_audit.py | mission-ledger.json | PRODUCER_ONLY | lifecycle_audit.py does not write back to mission-ledger |
| mission ledger → continuation decision | mission-ledger.json | check_continuation.py Check 1c | CONNECTED_AND_ENFORCED | Check 1c reads audit_pending, stop_status |
| ITERATION_REQUIRED → new taskcards | write_plan_lock.py | plan file | CONSUMER_MISSING | No function appends new taskcards after ITERATION_REQUIRED |
| continuation produced → consumed | continuation-signal.json | check_continuation.py | CONNECTED_AND_ENFORCED | Correctly consumed |
| mission-complete decision → stop | mission-ledger.stop_status | check_continuation.py | CONNECTED_AND_ENFORCED | MISSION_COMPLETE → STOP(MACHINERY_MISSION_COMPLETE) |

**Critical PRODUCER_ONLY boundaries (fixing required):**
1. `taskcards completed → post-execution audit` (RC-001: behavioral check absent)
2. `audit result → mission ledger update` (RC-002: no per-mission init or write-back)
3. `ITERATION_REQUIRED → new taskcards` (RC-004: no auto generation)

---

## Root Cause Registry

```yaml
root_causes:

  RC-001:
    id: RC-001
    title: lifecycle_audit AUDIT_PASS ignores mission-ledger behavioral iteration state
    symptoms:
      - All taskcards CLOSED + AUDIT_PASS fires immediately after one execution pass
      - No multi-iteration proof required before TERMINAL_CLOSED
    first_failing_boundary: "taskcards completed → post-execution behavioral audit"
    immediate_cause: "lifecycle_audit.py AUDIT_PASS condition never reads mission-ledger.json"
    structural_cause: "AUDIT_PASS was designed for current-moment correctness (task/gap status), not historical behavioral proof"
    evidence: "lifecycle_audit.py lines 597-603; no behavioral_iterations check; mission-ledger not imported"
    durable_fix: "Add Check B1 to lifecycle_audit.py: read .local/supervisor/machinery/mission-ledger.json; require current_behavioral_iterations >= behavioral_iterations_required"

  RC-002:
    id: RC-002
    title: New machinery plan creates no fresh mission-ledger entry
    symptoms:
      - VWL-001 never initialized a mission-ledger entry with its own mission_id
      - Old entry (machinery-lifecycle-healing-20260621) reused; iteration count is from a different mission
    first_failing_boundary: "mission identification → mission ledger initialization"
    structural_cause: "write_plan_lock.py --terminal --audit-gate does not initialize mission-ledger.json for new missions"
    durable_fix: "Add _init_machinery_mission_ledger(mission_id, plan_path) call at start of write_plan_lock execution for machinery plans"

  RC-003:
    id: RC-003
    title: G4 guard (sprint audit freshness) is non-blocking when audit log absent
    symptoms:
      - sprint-audit-log.json can be absent entirely; G4 gracefully skips
      - AUDIT_PASS fires even when no post-execution audit log exists
    structural_cause: "lifecycle_audit.py line 347: guard G4 checks `if audit_log_path.exists()` and skips gracefully when absent"
    evidence: "lifecycle_audit.py lines 333-365; MEDIUM severity; non-blocking"
    durable_fix: "Escalate G4 to CRITICAL when sprint-audit-log.json is completely absent (not stale but missing)"

  RC-004:
    id: RC-004
    title: No automatic taskcard generation when ITERATION_REQUIRED fires
    symptoms:
      - write_plan_lock writes ITERATION_REQUIRED lock
      - check_continuation returns CONTINUE
      - But plan file has NO new taskcards — agent must manually decide what to do next
    structural_cause: "No generate_behavioral_gap_taskcards() function exists in lifecycle_audit.py or write_plan_lock.py"
    durable_fix: "Add generate_behavioral_gap_taskcards(findings, plan_path) that appends new taskcard entries to the plan file with status OPEN"

  RC-005:
    id: RC-005
    title: MACHINERY_AUDIT_REQUIRED stop in check_continuation has no explicit routing instruction
    symptoms:
      - check_continuation returns STOP reason=MACHINERY_AUDIT_REQUIRED
      - Agent may interpret this as a terminal stop rather than route to audit
    structural_cause: "check_continuation.py returns stop verdict without next_action field"
    durable_fix: "Add next_action: 'run lifecycle_audit.py --mission-id <X>' to MACHINERY_AUDIT_REQUIRED stop output"

  RC-006:
    id: RC-006
    title: No V_MACH_* governance validators enforce behavioral iteration minimum
    symptoms:
      - Machinery plans can close at iteration=0 with no validator firing
      - No governance enforcement of post-execution audit requirement
    structural_cause: "governance_validators_ext4.py has no machinery-specific validators"
    durable_fix: "Add V_MACH_AUDIT_AFTER_EXEC, V_MACH_ITERATION_PROOF, V_MACH_CONTINUATION_CONSUMED, V_MACH_TASK_VS_MISSION"
```

---

## Stable-ID Registry

```yaml
stable_ids:
  mission:
    VELVET-SWINGING-WREATH-001: "Machinery iteration failure and lifecycle healing plan"
  root_causes:
    RC-001: "lifecycle_audit AUDIT_PASS ignores mission-ledger behavioral iteration state"
    RC-002: "New machinery plan creates no fresh mission-ledger entry"
    RC-003: "G4 guard non-blocking when audit log absent"
    RC-004: "No automatic taskcard generation on ITERATION_REQUIRED"
    RC-005: "MACHINERY_AUDIT_REQUIRED stop has no routing instruction"
    RC-006: "No V_MACH_* governance validators"
  gates:
    LIF-0: "Failed Run Reconstructed"
    LIF-1: "Expected Workflow Identified"
    LIF-2: "Producer-Consumer Map Complete"
    LIF-3: "First Failing Boundary Proven"
    LIF-4: "Stop-Condition Defects Proven"
    LIF-5: "Task vs Mission State Corrected"
    LIF-6: "Target Lifecycle Designed"
    LIF-7: "Mission Ledger Implemented"
    LIF-8: "Audit Consumer Implemented"
    LIF-9: "Continuation Consumer Implemented"
    LIF-10: "Plan Reopening and Task Regeneration Proven"
    LIF-11: "Closeout and Iteration Stop Defects Removed"
    LIF-12: "Single Iteration Pilot Proven"
    LIF-13: "Multi-Iteration Pilot Proven"
    LIF-14: "Interrupted Run Recovery Proven"
    LIF-15: "Lane Isolation Proven"
    LIF-16: "Idempotent Rerun Proven"
    LIF-17: "Autonomous Unattended Loop Proven"
    LIF-18: "Mission-Aware Stop Proven"
    LIF-19: "Authoritative Plan Ready"
    LIF-20: "Execution Handoff Ready"
  taskcards:
    TC-VWR-001: "forensics-and-orientation"
    TC-VWR-002: "producer-consumer-audit"
    TC-VWR-003: "check-b1-behavioral-iteration"
    TC-VWR-004: "mission-ledger-initialization"
    TC-VWR-005: "taskcard-generation-on-iteration-required"
    TC-VWR-006: "stop-condition-guard-repair"
    TC-VWR-007: "regression-validators-v-mach"
    TC-VWR-008: "pilot-a-single-iteration"
    TC-VWR-009: "pilot-h-multi-iteration"
    TC-VWR-010: "stable-id-artifacts"
    TC-VWR-011: "execution-handoff-finalization"
    TC-VWR-CLOSE: "lifecycle-audit-gate-and-closure"
```

---

## Machine State Model

### Parent taskcard states

```
PROPOSED → READY → IN_PROGRESS → CHILDREN_IN_PROGRESS → INTEGRATION_PENDING
→ VERIFIED → SCORED → CLOSED
          ↘ BLOCKED → READY
          ↘ BLOCKED_EXTERNAL
          ↘ DEFERRED_WITH_REASON
```

### Child taskcard states

```
TODO → READY → IN_PROGRESS → IMPLEMENTED → VERIFIED → SCORED → CLOSED
                           ↘ REROUTED → IN_PROGRESS
                           ↘ BLOCKED → READY
                           ↘ BLOCKED_EXTERNAL
                           ↘ DEFERRED_WITH_REASON
```

### Micro-step states

```
PENDING → READY → ACTIVE → COMPLETE
                         ↘ FAILED → READY
                         ↘ BLOCKED → READY
                         ↘ SKIPPED_NOT_APPLICABLE (requires reason)
```

### Invalid transitions (explicitly blocked)

- TODO → CLOSED (must pass through IMPLEMENTED and VERIFIED)
- IMPLEMENTED → CLOSED (must be VERIFIED)
- child CLOSED while required micro-steps PENDING/ACTIVE
- parent CLOSED while mandatory children not CLOSED
- REROUTED → CLOSED without rework completion
- BLOCKED_EXTERNAL → CLOSED without unblock evidence

---

## Taskcard Status Table

_lifecycle_audit.py reads this 2-column table. Exactly 2 pipe-separated columns required._

| Taskcard | Status |
|----------|--------|
| TC-VWR-001 | OPEN |
| TC-VWR-001-01 | OPEN |
| TC-VWR-001-02 | OPEN |
| TC-VWR-001-03 | OPEN |
| TC-VWR-001-04 | OPEN |
| TC-VWR-001-05 | OPEN |
| TC-VWR-002 | OPEN |
| TC-VWR-002-01 | OPEN |
| TC-VWR-002-02 | OPEN |
| TC-VWR-003 | OPEN |
| TC-VWR-003-01 | OPEN |
| TC-VWR-003-02 | OPEN |
| TC-VWR-003-03 | OPEN |
| TC-VWR-003-04 | OPEN |
| TC-VWR-004 | OPEN |
| TC-VWR-004-01 | OPEN |
| TC-VWR-004-02 | OPEN |
| TC-VWR-004-03 | OPEN |
| TC-VWR-005 | OPEN |
| TC-VWR-005-01 | OPEN |
| TC-VWR-005-02 | OPEN |
| TC-VWR-005-03 | OPEN |
| TC-VWR-006 | OPEN |
| TC-VWR-006-01 | OPEN |
| TC-VWR-006-02 | OPEN |
| TC-VWR-006-03 | OPEN |
| TC-VWR-007 | OPEN |
| TC-VWR-007-01 | OPEN |
| TC-VWR-007-02 | OPEN |
| TC-VWR-007-03 | OPEN |
| TC-VWR-007-04 | OPEN |
| TC-VWR-007-05 | OPEN |
| TC-VWR-008 | OPEN |
| TC-VWR-008-01 | OPEN |
| TC-VWR-008-02 | OPEN |
| TC-VWR-008-03 | OPEN |
| TC-VWR-009 | OPEN |
| TC-VWR-009-01 | OPEN |
| TC-VWR-009-02 | OPEN |
| TC-VWR-009-03 | OPEN |
| TC-VWR-009-04 | OPEN |
| TC-VWR-010 | OPEN |
| TC-VWR-010-01 | OPEN |
| TC-VWR-010-02 | OPEN |
| TC-VWR-011 | OPEN |
| TC-VWR-011-01 | OPEN |
| TC-VWR-011-02 | OPEN |
| TC-VWR-011-03 | OPEN |
| TC-VWR-CLOSE | OPEN |

---

## Execution DAG

```
STEP-0 (plan migration) → TC-VWR-001 → TC-VWR-002
                                            ↓
                                     TC-VWR-003 → TC-VWR-004 → TC-VWR-005
                                                             ↓           ↓
                                                       TC-VWR-006    TC-VWR-007
                                                                ↘         ↙
                                                             TC-VWR-008
                                                                  ↓
                                                             TC-VWR-009
                                                                  ↓
                                                             TC-VWR-010
                                                                  ↓
                                                             TC-VWR-011
                                                                  ↓
                                                            TC-VWR-CLOSE
```

**Parallel-safe tasks:**
- TC-VWR-006 and TC-VWR-007 may execute in parallel (different files: lifecycle_audit.py vs governance_validators_ext4.py)
- TC-VWR-010 may begin after TC-VWR-001 (does not depend on implementation)

**File ownership locks (prevent conflicts):**

| File | Owner taskcard |
|------|---------------|
| `tools/supervisor/lifecycle_audit.py` | TC-VWR-003, TC-VWR-006 (sequential) |
| `tools/supervisor/write_plan_lock.py` | TC-VWR-004 |
| `tools/supervisor/check_continuation.py` | TC-VWR-005 |
| `tools/supervisor/governance_validators_ext4.py` | TC-VWR-007 |
| `tools/supervisor/governance_validator_runner.py` | TC-VWR-007 |
| `.local/supervisor/machinery/mission-ledger.json` | TC-VWR-004 writes; TC-VWR-003 reads |
| `tests/supervisor/pilots/` | TC-VWR-008, TC-VWR-009 |
| `plans/.claude/velvet-swinging-wreath-artifacts/` | TC-VWR-010 |

---

## TC-VWR-001 — Repository Orientation & Failed-Run Reconstruction

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Root causes:** RC-001, RC-002
**Gates:** LIF-0, LIF-1
**Depends:** STEP-0 (plan migration complete)
**Note:** Forensics sections §PRE-FILLED above were populated during the planning phase. TC-VWR-001 confirms these findings against HEAD and writes the in-repo plan amendment if any corrections are needed.

### TC-VWR-001-01 — Confirm lifecycle_audit.py has no behavioral iteration check

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-001

**Purpose:** Confirm RC-001 root cause at HEAD before implementing the fix.

**Scope:**
- Allowed: read `tools/supervisor/lifecycle_audit.py`
- Forbidden: modify any file

**Micro-steps:**

MS-VWR-001-01-01
- Action: Run `grep -n "behavioral_iter\|iteration_count\|mission_ledger" tools/supervisor/lifecycle_audit.py`
- Expected output: 0 matches (confirms no behavioral check exists)
- If matches found: record which functions exist and update §Root Cause Registry accordingly
- Next: MS-VWR-001-01-02

MS-VWR-001-01-02
- Action: Read `tools/supervisor/lifecycle_audit.py` lines 595-650 (AUDIT_PASS condition block)
- Expected output: AUDIT_PASS conditions listed — confirm no mission-ledger.json read
- Record: exact line numbers of AUDIT_PASS condition block in §Failed-Run Forensics
- Next: MS-VWR-001-01-03

MS-VWR-001-01-03
- Action: Read `tools/supervisor/lifecycle_audit.py` lines 333-370 (G4 guard)
- Expected output: Confirm `if audit_log_path.exists()` pattern (graceful skip when absent)
- Record: exact line number of the existence check in §Failed-Run Forensics
- Next: COMPLETE → close TC-VWR-001-01

**Acceptance checks:**
- Grep returns 0 matches for behavioral iteration fields
- AUDIT_PASS block does not import or read mission-ledger.json
- G4 confirms graceful skip

**Evidence:** grep output (record in plan amendment)

---

### TC-VWR-001-02 — Confirm mission-ledger.json state and VWL-001 absence

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-001

**Scope:**
- Allowed: read `.local/supervisor/machinery/mission-ledger.json`
- Forbidden: modify any file

**Micro-steps:**

MS-VWR-001-02-01
- Action: Read `.local/supervisor/machinery/mission-ledger.json`
- Expected output: JSON with mission_id = "machinery-lifecycle-healing-20260621" (old mission, not VWL-001)
- Record: mission_id, current_iteration, stop_status values
- If VWL-001 mission_id found: update RC-002 classification to RESOLVED
- Next: MS-VWR-001-02-02

MS-VWR-001-02-02
- Action: Grep `.local/supervisor/machinery/mission-ledger.json` for "VELVET-SWINGING-WREATH\|VWL-001"
- Expected output: 0 matches (confirms RC-002: new mission had no fresh ledger entry)
- Next: COMPLETE → close TC-VWR-001-02

**Acceptance checks:** mission_id is NOT VWL-001 or VELVET-SWINGING-WREATH-001

---

### TC-VWR-001-03 — Confirm last lifecycle-audit-results.json verdict

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-001

**Scope:**
- Allowed: read `.local/supervisor/lifecycle-audit-results.json`
- Forbidden: modify any file

**Micro-steps:**

MS-VWR-001-03-01
- Action: Read `.local/supervisor/lifecycle-audit-results.json`
- Confirm: `mission_id = "VAST-WEAVING-LAMPSON-001"`, `verdict = "AUDIT_PASS"`, `mission_complete = true`
- Record: `guard_results` field (expected: [] — no guards fired)
- If verdict is NOT AUDIT_PASS: update §Failed-Run Forensics with actual verdict
- Next: COMPLETE → close TC-VWR-001-03

---

### TC-VWR-001-04 — Write in-repo plan with forensics amendment

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-001

**Purpose:** Ensure the in-repo copy of this plan is up to date with forensics findings.

**Scope:**
- Allowed: write `plans/.claude/velvet-swinging-wreath.md`
- Forbidden: modify any implementation file

**Micro-steps:**

MS-VWR-001-04-01
- Action: Verify `plans/.claude/velvet-swinging-wreath.md` exists (STEP-0 migration complete)
- If not: run STEP-0 migration commands before continuing
- Next: MS-VWR-001-04-02

MS-VWR-001-04-02
- Action: Update §Failed-Run Forensics in `plans/.claude/velvet-swinging-wreath.md` with any corrections found in TC-VWR-001-01 through TC-VWR-001-03
- Expected: forensics section accurately reflects HEAD state
- Next: MS-VWR-001-04-03

MS-VWR-001-04-03
- Action: Update TC-VWR-001, TC-VWR-001-01, TC-VWR-001-02, TC-VWR-001-03, TC-VWR-001-04 status from OPEN → CLOSED in the Taskcard Status Table
- Next: COMPLETE → close TC-VWR-001-04, TC-VWR-001

**Parent acceptance criteria (TC-VWR-001):**
- All 4 child taskcards CLOSED
- §Failed-Run Forensics confirmed at HEAD (or corrected)
- §Producer-Consumer Boundary Table confirmed at HEAD (pre-filled values verified)
- Plan lock written to in-repo path

**Gates passed:** LIF-0, LIF-1

---

## TC-VWR-002 — Producer-Consumer Forensics Verification

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Root causes:** RC-001 through RC-004
**Gates:** LIF-2, LIF-3, LIF-4
**Depends:** TC-VWR-001

**Objective:** Verify the pre-filled Producer-Consumer Boundary Table against actual code and confirm
each boundary's real classification. Identify any corrections needed before implementation begins.

### TC-VWR-002-01 — Verify write_plan_lock.py auto-audit trigger

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-002

**Micro-steps:**

MS-VWR-002-01-01
- Action: Read `tools/supervisor/write_plan_lock.py` lines 280-330
- Confirm: `--audit-gate` path calls `lifecycle_audit.run_lifecycle_audit()` before writing TERMINAL_CLOSED
- Confirm: ITERATION_REQUIRED path writes ITERATION_REQUIRED lock (not TERMINAL_CLOSED)
- Record: exact function name called for lifecycle audit
- Next: MS-VWR-002-01-02

MS-VWR-002-01-02
- Action: Read `tools/supervisor/write_plan_lock.py` lines 162-180 (_should_require_audit function)
- Confirm: auto-detection logic (searches for TC- pattern in plan file)
- Record: conditions that bypass the audit gate (--skip-audit flag)
- Next: COMPLETE → close TC-VWR-002-01

---

### TC-VWR-002-02 — Verify check_continuation.py Check 1c routing

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-002

**Micro-steps:**

MS-VWR-002-02-01
- Action: Read `tools/supervisor/check_continuation.py` lines 362-400
- Confirm: `MACHINERY_AUDIT_REQUIRED` stop output format — does it have a `next_action` field?
- If no `next_action` field: confirm RC-005 (missing routing instruction)
- Record: exact JSON output structure for MACHINERY_AUDIT_REQUIRED stop
- Next: COMPLETE → close TC-VWR-002-02

**Parent acceptance criteria (TC-VWR-002):**
- Both children CLOSED
- Pre-filled boundary table confirmed or corrected at HEAD
- No surprise boundaries discovered that would invalidate the implementation plan

**Gates passed:** LIF-2, LIF-3, LIF-4

---

## TC-VWR-003 — Add Check B1: Behavioral Iteration Minimum to lifecycle_audit.py

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Root causes:** RC-001
**Gates:** LIF-5, LIF-8
**Depends:** TC-VWR-001, TC-VWR-002
**Files owned:** `tools/supervisor/lifecycle_audit.py`

**Objective:** Add a new guard Check B1 that reads `mission-ledger.json.current_behavioral_iterations`
and returns AUDIT_REQUIRES_ITERATION when the count is below `behavioral_iterations_required` (default: 2)
for plans with `plan_type: machinery_hardening`.

**Preserved behavior:**
- All existing AUDIT_PASS conditions (open tasks, gaps, G1/G2) remain unchanged
- Check B1 fires ONLY for plans with `plan_type: machinery_hardening` in their header
- Non-machinery plans (product deepening, etc.) are unaffected
- Existing AUDIT_PASS for VWL (old run) is not retroactively changed

### TC-VWR-003-01 — Locate plan_type detection in lifecycle_audit.py

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-003

**Micro-steps:**

MS-VWR-003-01-01
- Action: Read `tools/supervisor/lifecycle_audit.py` lines 1-100 to find plan_type parsing
- Expected: function like `_detect_plan_type(plan_path)` or inline regex on plan frontmatter
- If function exists: record its name and line number
- If none exists: Check B1 implementation must add plan_type detection from plan header
- Next: MS-VWR-003-01-02

MS-VWR-003-01-02
- Action: Read `tools/supervisor/lifecycle_audit.py` lines 100-200 to find where mission-ledger is (or is not) imported/read
- Confirm: no existing `mission_ledger` import or read
- Record: imports section (to know where to add mission-ledger read)
- Next: COMPLETE → close TC-VWR-003-01

---

### TC-VWR-003-02 — Add `_read_machinery_mission_ledger(mission_id)` helper

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-003
**Depends:** TC-VWR-003-01

**Purpose:** Add a safe-read helper that returns the mission-ledger entry for `mission_id` or a
default sentinel if the entry is absent or the file doesn't exist.

**Scope:**
- Allowed: edit `tools/supervisor/lifecycle_audit.py` — add one function
- Forbidden: modify any other file; modify existing AUDIT_PASS logic

**Micro-steps:**

MS-VWR-003-02-01
- Action: Read lifecycle_audit.py lines around the imports block — identify the correct insertion point for the new helper function
- Expected: find `import json`, `from pathlib import Path`, etc.
- Record: the line number just before the first class/function definition
- Next: MS-VWR-003-02-02

MS-VWR-003-02-02
- Action: Add the following function to `tools/supervisor/lifecycle_audit.py` (insert before first class definition):

```python
_MACHINERY_LEDGER_PATH = Path(".local/supervisor/machinery/mission-ledger.json")

def _read_machinery_mission_ledger(mission_id: str) -> dict:
    """Read mission ledger for a given mission_id. Returns sentinel on missing/invalid data."""
    _default = {"current_behavioral_iterations": 0, "behavioral_iterations_required": 2, "_sentinel": True}
    if not _MACHINERY_LEDGER_PATH.exists():
        return _default
    try:
        data = json.loads(_MACHINERY_LEDGER_PATH.read_text(encoding="utf-8"))
        if data.get("mission_id") != mission_id:
            return _default  # Stale entry from different mission — treat as 0 iterations
        return data
    except Exception:
        return _default
```

- Verify: function added at correct location, no syntax errors
- Next: MS-VWR-003-02-03

MS-VWR-003-02-03
- Action: Run `python -c "from tools.supervisor.lifecycle_audit import _read_machinery_mission_ledger; print('OK')"` from repo root
- Expected output: `OK`
- If ImportError: fix import path issues
- Next: COMPLETE → close TC-VWR-003-02

---

### TC-VWR-003-03 — Add `_check_behavioral_iteration_guard(mission_id, plan_type)` function

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-003
**Depends:** TC-VWR-003-02

**Purpose:** Add the Check B1 guard function that returns a guard finding when behavioral iterations
are below the required minimum.

**Scope:**
- Allowed: edit `tools/supervisor/lifecycle_audit.py` — add one function after `_read_machinery_mission_ledger`
- Forbidden: modify existing guard functions G1-G4; modify AUDIT_PASS logic yet

**Micro-steps:**

MS-VWR-003-03-01
- Action: Add the following function to `tools/supervisor/lifecycle_audit.py` after `_read_machinery_mission_ledger`:

```python
def _check_behavioral_iteration_guard(mission_id: str, plan_type: str) -> dict | None:
    """
    Check B1: Behavioral iteration minimum.
    For machinery_hardening plans only: require current_behavioral_iterations >= behavioral_iterations_required.
    Returns a CRITICAL guard finding if not met, or None if passed / not applicable.
    """
    if plan_type != "machinery_hardening":
        return None
    ledger = _read_machinery_mission_ledger(mission_id)
    current = ledger.get("current_behavioral_iterations", 0)
    required = ledger.get("behavioral_iterations_required", 2)
    if current < required:
        return {
            "guard_id": "GB1",
            "severity": "CRITICAL",
            "check": "behavioral_iteration_minimum",
            "current_behavioral_iterations": current,
            "behavioral_iterations_required": required,
            "mission_id": mission_id,
            "sentinel": ledger.get("_sentinel", False),
            "message": (
                f"Behavioral iteration minimum not met: {current}/{required} iterations completed. "
                "Mission-ledger may be absent or stale — treating as 0 iterations. "
                "Returning AUDIT_REQUIRES_ITERATION to prevent premature TERMINAL_CLOSED."
            ),
        }
    return None
```

- Verify: function added, no syntax errors
- Next: MS-VWR-003-03-02

MS-VWR-003-03-02
- Action: Run `python -c "from tools.supervisor.lifecycle_audit import _check_behavioral_iteration_guard; r = _check_behavioral_iteration_guard('X', 'machinery_hardening'); print(r['guard_id'])"` from repo root
- Expected: prints `GB1`
- If fails: fix import or function definition
- Next: COMPLETE → close TC-VWR-003-03

---

### TC-VWR-003-04 — Wire Check B1 into AUDIT_PASS condition block

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-003
**Depends:** TC-VWR-003-03

**Purpose:** Integrate Check B1 into the existing AUDIT_PASS evaluation logic.

**Scope:**
- Allowed: edit `tools/supervisor/lifecycle_audit.py` AUDIT_PASS block (lines ~595-610)
- Forbidden: remove or weaken existing G1/G2/G3/G4 guard logic; affect non-machinery plans

**Micro-steps:**

MS-VWR-003-04-01
- Action: Read `tools/supervisor/lifecycle_audit.py` lines 570-640 to identify:
  - The exact function that computes AUDIT_PASS (name + line range)
  - The exact location where guard_results are collected
  - The variable name that holds `plan_type`
  - The variable name that holds `mission_id`
- Record all four items
- Next: MS-VWR-003-04-02

MS-VWR-003-04-02
- Action: In the guard collection section of `run_lifecycle_audit()`, add after existing G1-G4 guard checks:

```python
# Check B1: Behavioral iteration minimum (machinery_hardening plans only)
_b1_finding = _check_behavioral_iteration_guard(mission_id or "", _plan_type or "")
if _b1_finding:
    guard_results.append(f"GB1:{_b1_finding['severity']}")
    findings.append(_b1_finding)
    has_critical_guard = True
```

- Note: `_plan_type` is the local variable holding plan_type; `mission_id` is the CLI arg
- If variable names differ, use actual names from MS-VWR-003-04-01 findings
- Next: MS-VWR-003-04-03

MS-VWR-003-04-03
- Action: Add plan_type detection from plan file header if not already present.
  In `run_lifecycle_audit()`, near the beginning (after plan_path is resolved):

```python
# Detect plan type from plan frontmatter
_plan_type = "unknown"
if plan_path and Path(plan_path).exists():
    _header_text = Path(plan_path).read_text(encoding="utf-8", errors="replace")[:2000]
    import re as _re
    _pt_match = _re.search(r'\*\*plan_type:\*\*\s+(\S+)', _header_text)
    if _pt_match:
        _plan_type = _pt_match.group(1)
```

- Verify: existing code doesn't already do this (if it does, skip and record)
- Next: MS-VWR-003-04-04

MS-VWR-003-04-04
- Action: Run the existing lifecycle_audit smoke test (if exists) or run:
  `python -c "import subprocess; result = subprocess.run(['python', 'tools/supervisor/lifecycle_audit.py', '--help'], capture_output=True, text=True); print(result.stdout[:200])"`
- Verify: tool still starts without error
- Next: COMPLETE → close TC-VWR-003-04

**Parent acceptance criteria (TC-VWR-003):**
- All 4 children CLOSED
- `_read_machinery_mission_ledger()` function exists in lifecycle_audit.py
- `_check_behavioral_iteration_guard()` function exists in lifecycle_audit.py
- Check B1 wired into AUDIT_PASS block
- Non-machinery plans unaffected (plan_type != "machinery_hardening" → guard returns None)
- lifecycle_audit.py imports without error

**Quality gates:**
- Requirement correctness: Check B1 only fires for machinery_hardening plans ≥ 4/5
- Implementation correctness: sentinel default of 0 iterations is safe ≥ 4/5
- Regression safety: non-machinery plans unaffected ≥ 4/5
- Test coverage: TC-VWR-008/009 pilots prove this end-to-end ≥ 4/5

**Gates passed:** LIF-5, LIF-8

---

## TC-VWR-004 — Mission-Ledger Initialization per Machinery Mission

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Root causes:** RC-002
**Gates:** LIF-7
**Depends:** TC-VWR-003
**Files owned:** `tools/supervisor/write_plan_lock.py`, `.local/supervisor/machinery/mission-ledger.json`

**Objective:** When `write_plan_lock.py --terminal --audit-gate` is called for a machinery plan,
automatically initialize (or refresh) a mission-ledger entry for the new mission_id, so that
Check B1 has a valid entry to read rather than a stale old mission entry.

### TC-VWR-004-01 — Add `_init_machinery_mission_ledger(mission_id, plan_path)` to write_plan_lock.py

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-004

**Micro-steps:**

MS-VWR-004-01-01
- Action: Read `tools/supervisor/write_plan_lock.py` lines 1-60 (imports + top-level constants)
- Record: where `lifecycle_audit` is imported; where `REPO_ROOT` is defined
- Next: MS-VWR-004-01-02

MS-VWR-004-01-02
- Action: Add `_init_machinery_mission_ledger(mission_id, plan_path)` function to `write_plan_lock.py`:

```python
def _init_machinery_mission_ledger(mission_id: str, plan_path: str | None) -> None:
    """Initialize or refresh mission-ledger.json for a new machinery mission.
    Only writes if the mission_id is different from the current ledger's mission_id.
    Preserves existing entry if mission_id matches (idempotent).
    """
    ledger_path = REPO_ROOT / ".local" / "supervisor" / "machinery" / "mission-ledger.json"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    # Read existing
    existing = {}
    if ledger_path.exists():
        try:
            existing = json.loads(ledger_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    # If same mission: preserve existing (idempotent)
    if existing.get("mission_id") == mission_id:
        return
    # New mission: initialize fresh entry
    import datetime
    new_entry = {
        "schema_version": "1.0",
        "mission_id": mission_id,
        "mission_type": "machinery_hardening",
        "authoritative_plan": plan_path or "",
        "current_iteration": 0,
        "current_stage": "EXECUTION",
        "last_completed_stage": None,
        "next_required_stage": "POST_EXECUTION_SPRINT_AUDIT",
        "active_taskcards": [],
        "rework_taskcards": [],
        "open_gaps": [],
        "closed_gaps": [],
        "audit_pending": True,
        "replan_pending": False,
        "execution_pending": False,
        "completion_audit_pending": False,
        "behavioral_iterations_required": 2,
        "current_behavioral_iterations": 0,
        "stop_status": "RUNNING",
        "stop_reason": None,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "state_digest": f"{mission_id}:iteration=0:stage=EXECUTION",
    }
    ledger_path.write_text(json.dumps(new_entry, indent=2) + "\n", encoding="utf-8")
```

- Verify: function added, no syntax errors
- Next: MS-VWR-004-01-03

MS-VWR-004-01-03
- Action: Identify where in `write_plan_lock.py` the audit-gate flow begins (lines 284-295 from research)
  and add a call to `_init_machinery_mission_ledger(mission_id, plan_path)` BEFORE calling lifecycle_audit:

```python
# Initialize machinery mission ledger for this mission (idempotent if same mission_id)
if track == "machinery" or _should_require_audit(plan_path):
    _init_machinery_mission_ledger(mission_id or "unknown", plan_path)
```

- Verify: call added at correct location (before lifecycle_audit call, not after)
- Next: COMPLETE → close TC-VWR-004-01

---

### TC-VWR-004-02 — Add `_increment_behavioral_iteration(mission_id)` to lifecycle_audit.py

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-004
**Depends:** TC-VWR-004-01

**Purpose:** After each successful execution sprint (all tasks pass, no ITERATION_REQUIRED), increment
`current_behavioral_iterations` in the mission-ledger. This enables Check B1 to eventually reach
the required minimum and allow AUDIT_PASS.

**Scope:**
- Allowed: edit `tools/supervisor/lifecycle_audit.py`
- Forbidden: modify write_plan_lock.py (handled by TC-VWR-004-01)

**Micro-steps:**

MS-VWR-004-02-01
- Action: Add `_increment_behavioral_iteration(mission_id)` function to `tools/supervisor/lifecycle_audit.py`
  after `_read_machinery_mission_ledger`:

```python
def _increment_behavioral_iteration(mission_id: str) -> int:
    """Increment current_behavioral_iterations in mission-ledger.json for mission_id.
    Returns the new iteration count. Safe to call multiple times (idempotent per call).
    """
    import datetime
    ledger_path = Path(".local/supervisor/machinery/mission-ledger.json")
    if not ledger_path.exists():
        return 0
    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception:
        return 0
    if data.get("mission_id") != mission_id:
        return 0
    data["current_behavioral_iterations"] = data.get("current_behavioral_iterations", 0) + 1
    data["audit_pending"] = False
    data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data["state_digest"] = f"{mission_id}:iteration={data['current_behavioral_iterations']}:stage=POST_EXECUTION_AUDIT"
    ledger_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data["current_behavioral_iterations"]
```

- Verify: function added, no syntax errors
- Next: MS-VWR-004-02-02

MS-VWR-004-02-02
- Action: Wire `_increment_behavioral_iteration` into `run_lifecycle_audit()`:
  When verdict is AUDIT_REQUIRES_ITERATION due to Check B1 ONLY (not other guards):
  DO NOT increment (iteration proof not yet complete).
  When verdict is AUDIT_PASS on a machinery_hardening plan (Check B1 passed):
  Call `_increment_behavioral_iteration(mission_id)` to record the completed cycle.

  Add after the verdict block (around line 605):
```python
# Increment behavioral iteration counter on successful AUDIT_PASS for machinery plans
if verdict == "AUDIT_PASS" and _plan_type == "machinery_hardening" and mission_id:
    _increment_behavioral_iteration(mission_id)
```

- Next: COMPLETE → close TC-VWR-004-02

---

### TC-VWR-004-03 — Add `next_action` field to MACHINERY_AUDIT_REQUIRED stop output

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-004
**Depends:** TC-VWR-002-02
**Files owned:** `tools/supervisor/check_continuation.py`

**Purpose:** Fix RC-005 by adding explicit routing instruction to MACHINERY_AUDIT_REQUIRED stop output.

**Micro-steps:**

MS-VWR-004-03-01
- Action: Read `tools/supervisor/check_continuation.py` lines 380-400
- Find: the exact `_stop("MACHINERY_AUDIT_REQUIRED", ...)` call
- Record: exact call signature and surrounding context
- Next: MS-VWR-004-03-02

MS-VWR-004-03-02
- Action: Add `next_action` field to the MACHINERY_AUDIT_REQUIRED stop dict:

```python
# In _stop("MACHINERY_AUDIT_REQUIRED", ...) call, add extra kwargs:
next_action="python tools/supervisor/lifecycle_audit.py --mission-id <MISSION_ID> --plan-path <PLAN_PATH>",
next_action_description="Run post-execution lifecycle audit. Do NOT treat this as a terminal stop.",
```

- If the `_stop` function doesn't accept kwargs: add them to the output JSON dict before returning
- Next: COMPLETE → close TC-VWR-004-03

**Parent acceptance criteria (TC-VWR-004):**
- All 3 children CLOSED
- `_init_machinery_mission_ledger()` exists in write_plan_lock.py
- `_increment_behavioral_iteration()` exists in lifecycle_audit.py
- `next_action` field added to MACHINERY_AUDIT_REQUIRED stop output
- lifecycle_audit.py and write_plan_lock.py import without error

**Gates passed:** LIF-7

---

## TC-VWR-005 — Automatic Taskcard Generation from Behavioral Audit Gaps

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Root causes:** RC-004
**Gates:** LIF-9, LIF-10
**Depends:** TC-VWR-003, TC-VWR-004
**Files owned:** `tools/supervisor/lifecycle_audit.py`, `tools/supervisor/write_plan_lock.py`

**Objective:** When lifecycle_audit returns AUDIT_REQUIRES_ITERATION (specifically due to Check B1),
automatically append new taskcard entries to the plan file so the agent has concrete next work to
execute — rather than having to manually invent follow-up taskcards.

### TC-VWR-005-01 — Add `generate_behavioral_gap_taskcards(findings, plan_path)` to lifecycle_audit.py

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-005

**Micro-steps:**

MS-VWR-005-01-01
- Action: Add the following function to `tools/supervisor/lifecycle_audit.py`:

```python
def generate_behavioral_gap_taskcards(findings: list, plan_path: str, mission_id: str = "") -> list[str]:
    """
    For each Check-B1 behavioral gap finding, append a new taskcard to the plan file.
    Returns list of created taskcard IDs. Idempotent: skips taskcard IDs already in the plan.
    """
    b1_findings = [f for f in findings if f.get("guard_id") == "GB1"]
    if not b1_findings:
        return []
    plan_file = Path(plan_path)
    if not plan_file.exists():
        return []
    plan_text = plan_file.read_text(encoding="utf-8")
    created_ids = []
    for i, finding in enumerate(b1_findings, start=1):
        current_iter = finding.get("current_behavioral_iterations", 0)
        required_iter = finding.get("behavioral_iterations_required", 2)
        tc_id = f"TC-{mission_id.split('-')[0] if mission_id else 'VWR'}-BEH-{current_iter + 1:03d}"
        # Idempotency: skip if already in plan
        if tc_id in plan_text:
            continue
        # Append taskcard to plan
        taskcard_text = f"""
---

## {tc_id} — Behavioral Iteration {current_iter + 1} of {required_iter}

**Type:** CHILD (auto-generated by lifecycle_audit Check B1)
**Status:** OPEN
**Parent:** BEHAVIORAL_ITERATION_GATE
**Auto-generated:** true
**Iteration:** {current_iter + 1} / {required_iter}

### Objective
Execute and verify one complete audit-execute-reaudit cycle to satisfy behavioral iteration proof.
This taskcard was auto-generated because `current_behavioral_iterations={current_iter}` < `required={required_iter}`.

### Implementation steps

1. Execute any pending or re-opened implementation taskcards in this plan
2. Run post-execution verification (focused + integration)
3. Run: `python tools/supervisor/lifecycle_audit.py --mission-id {mission_id} --plan-path {plan_path}`
4. If AUDIT_REQUIRES_ITERATION again: update mission-ledger audit_pending=True, continue to next iteration
5. If AUDIT_PASS: close this taskcard; write_plan_lock --terminal --audit-gate

### Verification

```bash
python tools/supervisor/lifecycle_audit.py \\
  --mission-id {mission_id} \\
  --plan-path {plan_path}
```

Expected: verdict advances toward AUDIT_PASS (behavioral_iterations increases)

"""
        plan_text += taskcard_text
        # Add to status table
        plan_text = plan_text.replace(
            f"| {tc_id} | OPEN |",
            f"| {tc_id} | OPEN |",
        )
        # Insert into status table if not present
        if f"| {tc_id} |" not in plan_text:
            plan_text = plan_text.replace(
                "| TC-VWR-CLOSE | OPEN |",
                f"| {tc_id} | OPEN |\n| TC-VWR-CLOSE | OPEN |",
            )
        created_ids.append(tc_id)
    if created_ids:
        plan_file.write_text(plan_text, encoding="utf-8")
    return created_ids
```

- Verify: function added, no syntax errors
- Next: MS-VWR-005-01-02

MS-VWR-005-01-02
- Action: Run `python -c "from tools.supervisor.lifecycle_audit import generate_behavioral_gap_taskcards; print('OK')"` from repo root
- Expected output: `OK`
- Next: COMPLETE → close TC-VWR-005-01

---

### TC-VWR-005-02 — Wire taskcard generation into write_plan_lock.py ITERATION_REQUIRED path

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-005
**Depends:** TC-VWR-005-01

**Micro-steps:**

MS-VWR-005-02-01
- Action: Read `tools/supervisor/write_plan_lock.py` lines 305-340 (ITERATION_REQUIRED path)
- Find: where audit_result is received and status = "ITERATION_REQUIRED" is written
- Record: exact location to insert taskcard generation call
- Next: MS-VWR-005-02-02

MS-VWR-005-02-02
- Action: In `write_plan_lock.py`, after `status = "ITERATION_REQUIRED"` is set, add:

```python
# Auto-generate behavioral gap taskcards in the plan file
try:
    from tools.supervisor.lifecycle_audit import generate_behavioral_gap_taskcards
    _created = generate_behavioral_gap_taskcards(
        audit_result.get("findings", []),
        plan_path or "",
        mission_id=mission_id or "",
    )
    if _created:
        print(f"[write_plan_lock] Auto-generated {len(_created)} behavioral gap taskcards: {_created}")
except Exception as _e:
    print(f"[write_plan_lock] WARNING: taskcard generation failed: {_e}")
```

- Verify: call added correctly; no syntax errors
- Next: COMPLETE → close TC-VWR-005-02

---

### TC-VWR-005-03 — Write test: test_taskcard_generation.py

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-005
**Depends:** TC-VWR-005-01

**Micro-steps:**

MS-VWR-005-03-01
- Action: Check if `tests/supervisor/test_taskcard_generation.py` exists
- If yes: read it to understand existing tests; add new scenario if not present
- If no: create the file
- Next: MS-VWR-005-03-02

MS-VWR-005-03-02
- Action: Write `tests/supervisor/test_taskcard_generation.py` with these scenarios:

```python
"""Tests for generate_behavioral_gap_taskcards() in lifecycle_audit.py"""
import json
import pytest
from pathlib import Path


@pytest.fixture
def tmp_plan(tmp_path):
    """Minimal machinery plan with status table."""
    plan_content = """# test-plan
**plan_type:** machinery_hardening
**mission_id:** TEST-MISSION-001

## Taskcard Status Table

| Taskcard | Status |
|----------|--------|
| TC-TEST-001 | CLOSED |
| TC-VWR-CLOSE | OPEN |
"""
    p = tmp_path / "test-plan.md"
    p.write_text(plan_content, encoding="utf-8")
    return str(p)


def test_generates_taskcard_for_b1_finding(tmp_plan):
    from tools.supervisor.lifecycle_audit import generate_behavioral_gap_taskcards
    findings = [{
        "guard_id": "GB1",
        "current_behavioral_iterations": 0,
        "behavioral_iterations_required": 2,
    }]
    created = generate_behavioral_gap_taskcards(findings, tmp_plan, mission_id="TEST")
    assert len(created) == 1
    assert "TC-TEST-BEH-001" in created[0]
    # Verify plan file updated
    text = Path(tmp_plan).read_text(encoding="utf-8")
    assert "TC-TEST-BEH-001" in text


def test_idempotent_no_duplicate(tmp_plan):
    from tools.supervisor.lifecycle_audit import generate_behavioral_gap_taskcards
    findings = [{"guard_id": "GB1", "current_behavioral_iterations": 0, "behavioral_iterations_required": 2}]
    created1 = generate_behavioral_gap_taskcards(findings, tmp_plan, mission_id="TEST")
    created2 = generate_behavioral_gap_taskcards(findings, tmp_plan, mission_id="TEST")
    assert len(created1) == 1
    assert len(created2) == 0  # Already in plan, skipped


def test_no_taskcards_for_non_b1_findings(tmp_plan):
    from tools.supervisor.lifecycle_audit import generate_behavioral_gap_taskcards
    findings = [{"guard_id": "G1", "severity": "CRITICAL"}]
    created = generate_behavioral_gap_taskcards(findings, tmp_plan, mission_id="TEST")
    assert created == []
```

- Run: `.venv/Scripts/pytest tests/supervisor/test_taskcard_generation.py -v`
- Expected: 3 passed
- If failed: fix the implementation in TC-VWR-005-01
- Next: COMPLETE → close TC-VWR-005-03

**Parent acceptance criteria (TC-VWR-005):**
- All 3 children CLOSED
- `generate_behavioral_gap_taskcards()` exists and passes all 3 tests
- write_plan_lock.py calls taskcard generation on ITERATION_REQUIRED
- Idempotency confirmed (duplicate taskcard prevention)

**Gates passed:** LIF-9, LIF-10

---

## TC-VWR-006 — Stop-Condition Guard Repair

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Root causes:** RC-003
**Gates:** LIF-11
**Depends:** TC-VWR-003
**Files owned:** `tools/supervisor/lifecycle_audit.py`
**Parallel-safe with:** TC-VWR-007

**Objective:** Fix Guard G4 to be CRITICAL (not MEDIUM) when `sprint-audit-log.json` is completely
absent, and add an iteration-limit guard that blocks AUDIT_PASS when behavioral iterations are below
minimum even when MAX_ITERATIONS is reached.

### TC-VWR-006-01 — Escalate G4 severity when sprint-audit-log.json is absent

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-006

**Micro-steps:**

MS-VWR-006-01-01
- Action: Read `tools/supervisor/lifecycle_audit.py` lines 333-370 (G4 guard)
- Record: exact line numbers of `if audit_log_path.exists()` check and the graceful-skip path
- Next: MS-VWR-006-01-02

MS-VWR-006-01-02
- Action: In G4 guard, change the graceful-skip branch:

Current behavior (approximate):
```python
if not audit_log_path.exists():
    # Skip G4 gracefully — no audit log found
    return None  # or equivalent
```

New behavior:
```python
if not audit_log_path.exists():
    # ESCALATE: absent audit log = audit never ran = behavioral proof absent
    return {
        "guard_id": "G4",
        "severity": "CRITICAL",  # was: MEDIUM / graceful skip
        "check": "sprint_audit_log_absent",
        "message": "sprint-audit-log.json does not exist. Post-execution audit was never run. "
                   "Cannot authorize TERMINAL_CLOSED without behavioral audit evidence.",
        "audit_log_expected": str(audit_log_path),
    }
```

- Verify: change made, no syntax errors, existing MEDIUM severity for stale-but-present log preserved
- Next: COMPLETE → close TC-VWR-006-01

---

### TC-VWR-006-02 — Write test for G4 absent-log escalation

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-006
**Depends:** TC-VWR-006-01

**Micro-steps:**

MS-VWR-006-02-01
- Action: Check if `tests/supervisor/test_lifecycle_guards.py` exists
- If not: create it
- Next: MS-VWR-006-02-02

MS-VWR-006-02-02
- Action: Add the following test to `tests/supervisor/test_lifecycle_guards.py`:

```python
"""Tests for lifecycle_audit guards."""
import pytest
from pathlib import Path
from unittest.mock import patch


def test_g4_critical_when_audit_log_absent(tmp_path):
    """G4 guard must return CRITICAL finding when sprint-audit-log.json does not exist."""
    from tools.supervisor.lifecycle_audit import check_sprint_audit_guard
    # Provide a path to an audit log that does NOT exist
    missing_log = tmp_path / "sprint-audit-log.json"
    result = check_sprint_audit_guard(audit_log_path=missing_log)
    assert result is not None, "G4 should fire when audit log is absent"
    assert result["severity"] == "CRITICAL", f"Expected CRITICAL, got {result.get('severity')}"


def test_g4_medium_when_audit_log_stale(tmp_path):
    """G4 guard must return MEDIUM (not CRITICAL) when audit log exists but is stale."""
    import time
    from tools.supervisor.lifecycle_audit import check_sprint_audit_guard
    stale_log = tmp_path / "sprint-audit-log.json"
    stale_log.write_text('{"stage": "audit"}')
    # Touch evidence-review to be newer than audit log
    time.sleep(0.01)
    evidence = tmp_path / "evidence-review.json"
    evidence.write_text('{"verdict": "ACCEPTED"}')
    result = check_sprint_audit_guard(
        audit_log_path=stale_log,
        evidence_review_path=evidence,
    )
    if result is not None:
        assert result["severity"] == "MEDIUM", f"Stale log should be MEDIUM, got {result.get('severity')}"
```

- Run: `.venv/Scripts/pytest tests/supervisor/test_lifecycle_guards.py -v`
- Expected: tests pass (or fix implementation if they fail)
- Note: if `check_sprint_audit_guard` function signature doesn't accept `audit_log_path` param, adapt the test to call lifecycle_audit differently
- Next: COMPLETE → close TC-VWR-006-02

---

### TC-VWR-006-03 — Add iteration-limit guard to lifecycle_audit.py

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-006
**Depends:** TC-VWR-006-01

**Purpose:** Prevent MAX_ITERATIONS from silently producing AUDIT_PASS when behavioral proof is incomplete.

**Micro-steps:**

MS-VWR-006-03-01
- Action: Read `tools/supervisor/lifecycle_audit.py` G3 guard (lines 308-330)
- Confirm: G3 is MEDIUM severity (GUARD_WARN only)
- Note: G3 fires when `stop_reason` contains `MAX_ITERATIONS`
- Record: exact condition check in G3
- Next: MS-VWR-006-03-02

MS-VWR-006-03-02
- Action: In `run_lifecycle_audit()`, after collecting guard results, add:

```python
# Iteration-limit + behavioral iteration cross-check
# If we hit MAX_ITERATIONS AND behavioral iterations are still below minimum,
# escalate to CRITICAL to prevent premature AUDIT_PASS
if any("G3" in g for g in guard_results):  # G3 fired (iteration limit)
    _ledger = _read_machinery_mission_ledger(mission_id or "")
    _current_b = _ledger.get("current_behavioral_iterations", 0)
    _required_b = _ledger.get("behavioral_iterations_required", 2)
    if _current_b < _required_b:
        guard_results.append("G3X:CRITICAL")
        findings.append({
            "guard_id": "G3X",
            "severity": "CRITICAL",
            "check": "iteration_limit_without_behavioral_proof",
            "message": f"Iteration limit reached but behavioral iterations ({_current_b}) < required ({_required_b}). "
                       "Blocking AUDIT_PASS to prevent false mission completion.",
        })
        has_critical_guard = True
```

- Verify: change made, no syntax errors
- Next: COMPLETE → close TC-VWR-006-03

**Parent acceptance criteria (TC-VWR-006):**
- All 3 children CLOSED
- G4 returns CRITICAL (not skip) when sprint-audit-log.json absent
- G3X fires when MAX_ITERATIONS + behavioral proof incomplete
- Tests pass

**Gates passed:** LIF-11

---

## TC-VWR-007 — Add V_MACH_* Regression Validators

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Root causes:** RC-006
**Gates:** LIF-6
**Depends:** TC-VWR-005, TC-VWR-006
**Files owned:** `tools/supervisor/governance_validators_ext4.py`, `tools/supervisor/governance_validator_runner.py`
**Parallel-safe with:** TC-VWR-006

**Objective:** Add 4 V_MACH_* validators to `governance_validators_ext4.py` so that every future
machinery sprint is automatically checked for lifecycle violation. Update expected_count: 167 → 171.

**CRITICAL NOTE:** The current expected_count in governance_validator_runner.py is 167, NOT 165
as stated in the initial plan draft. This task adds 4 validators, bringing total to 171.

### TC-VWR-007-01 — Read current governance_validators_ext4.py structure

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-007

**Micro-steps:**

MS-VWR-007-01-01
- Action: Read `tools/supervisor/governance_validators_ext4.py` lines 1-60
- Record: current highest validator number (expected: V127), validator function signature pattern
- Confirm: no existing V_MACH_* validators
- Next: MS-VWR-007-01-02

MS-VWR-007-01-02
- Action: Read `tools/supervisor/governance_validator_runner.py` to find `expected_count`
- Expected: `expected_count = 167` or similar
- Record: exact line number and current value
- Next: COMPLETE → close TC-VWR-007-01

---

### TC-VWR-007-02 — Add V_MACH_AUDIT_AFTER_EXEC validator

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-007
**Depends:** TC-VWR-007-01

**Micro-steps:**

MS-VWR-007-02-01
- Action: Append to `tools/supervisor/governance_validators_ext4.py` (use next available V-number, e.g. V150 if V149 is highest):

```python
def validate_mach_audit_after_execution(repo_root: Path | None = None) -> list[dict]:
    """V_MACH_AUDIT_AFTER_EXEC: For machinery sprints, require lifecycle-audit-results.json
    to have been updated within 30 minutes of the declaration timestamp.
    WARN severity — does not block (advisory gate).
    """
    findings = []
    _root = repo_root or REPO_ROOT
    audit_results = _root / ".local" / "supervisor" / "lifecycle-audit-results.json"
    declaration_dir = _root / ".local" / "evidences"
    if not audit_results.exists():
        findings.append({
            "validator": "V_MACH_AUDIT_AFTER_EXEC",
            "severity": "WARN",
            "message": "lifecycle-audit-results.json not found — lifecycle audit may not have run",
            "path": str(audit_results),
        })
    return findings
```

- Next: COMPLETE → close TC-VWR-007-02

---

### TC-VWR-007-03 — Add V_MACH_ITERATION_PROOF validator

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-007
**Depends:** TC-VWR-007-01

**Micro-steps:**

MS-VWR-007-03-01
- Action: Append V_MACH_ITERATION_PROOF validator to `tools/supervisor/governance_validators_ext4.py`:

```python
def validate_mach_iteration_proof(repo_root: Path | None = None) -> list[dict]:
    """V_MACH_ITERATION_PROOF: For machinery plans at TERMINAL_CLOSED,
    require current_behavioral_iterations >= behavioral_iterations_required in mission-ledger.json.
    BLOCK severity — prevents false mission completion.
    """
    findings = []
    _root = repo_root or REPO_ROOT
    # Check if any plan lock is TERMINAL_CLOSED
    lock_dir = _root / ".local" / "supervisor" / "plan-locks"
    ledger_path = _root / ".local" / "supervisor" / "machinery" / "mission-ledger.json"
    if not lock_dir.exists():
        return findings
    for lock_file in lock_dir.glob("*.json"):
        try:
            lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if lock_data.get("status") != "TERMINAL_CLOSED":
            continue
        # Check behavioral iterations
        if not ledger_path.exists():
            continue
        try:
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        current = ledger.get("current_behavioral_iterations", 0)
        required = ledger.get("behavioral_iterations_required", 2)
        if current < required:
            findings.append({
                "validator": "V_MACH_ITERATION_PROOF",
                "severity": "BLOCK",
                "message": f"TERMINAL_CLOSED written but behavioral_iterations {current} < {required}. "
                           "Possible premature mission completion.",
                "lock_file": str(lock_file),
                "current_behavioral_iterations": current,
                "behavioral_iterations_required": required,
            })
    return findings
```

- Next: COMPLETE → close TC-VWR-007-03

---

### TC-VWR-007-04 — Add V_MACH_TASK_VS_MISSION validator

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-007
**Depends:** TC-VWR-007-01

**Micro-steps:**

MS-VWR-007-04-01
- Action: Append V_MACH_TASK_VS_MISSION validator to `tools/supervisor/governance_validators_ext4.py`:

```python
def validate_mach_task_vs_mission(repo_root: Path | None = None) -> list[dict]:
    """V_MACH_TASK_VS_MISSION: Block any sprint that closes the final machinery plan taskcard
    without lifecycle-audit-results.json showing mission_complete: true.
    BLOCK severity.
    """
    findings = []
    _root = repo_root or REPO_ROOT
    audit_results_path = _root / ".local" / "supervisor" / "lifecycle-audit-results.json"
    if not audit_results_path.exists():
        return findings
    try:
        audit = json.loads(audit_results_path.read_text(encoding="utf-8"))
    except Exception:
        return findings
    if not audit.get("mission_complete", True):
        # mission_complete is False while plan is supposedly complete
        if audit.get("all_taskcards_closed"):
            findings.append({
                "validator": "V_MACH_TASK_VS_MISSION",
                "severity": "BLOCK",
                "message": "All taskcards closed but lifecycle-audit mission_complete=False. "
                           "Task completion ≠ mission completion. Post-execution audit required.",
            })
    return findings
```

- Next: COMPLETE → close TC-VWR-007-04

---

### TC-VWR-007-05 — Register validators and update expected_count

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-007
**Depends:** TC-VWR-007-02, TC-VWR-007-03, TC-VWR-007-04

**Micro-steps:**

MS-VWR-007-05-01
- Action: In `tools/supervisor/governance_validators_ext4.py`, add the 3 new validators
  to the registry list (the list that `governance_validator_runner.py` imports to discover validators)
- Read the file to find the registry list/dict pattern
- Add entries: `validate_mach_audit_after_execution`, `validate_mach_iteration_proof`, `validate_mach_task_vs_mission`
- (V_MACH_CONTINUATION_CONSUMED is deferred: it requires runtime signal tracking not available statically)
- Next: MS-VWR-007-05-02

MS-VWR-007-05-02
- Action: Update `tools/supervisor/governance_validator_runner.py`:
  Find `expected_count` (currently 167) and update to 170 (167 + 3 new validators)
- Note: V_MACH_CONTINUATION_CONSUMED deferred → only 3 not 4 added
- If the test assertion also has expected_count: update it to match
- Next: MS-VWR-007-05-03

MS-VWR-007-05-03
- Action: Run `python tools/supervisor/governance_validator_runner.py --count-only` (or equivalent)
  to verify validator count matches expected_count
- Expected output: count = 170 (or whatever was determined by MS-VWR-007-01)
- If count mismatch: audit the registry list for missing or duplicate entries
- Next: COMPLETE → close TC-VWR-007-05

**Parent acceptance criteria (TC-VWR-007):**
- All 5 children CLOSED
- 3 new V_MACH_* validators in governance_validators_ext4.py
- expected_count updated correctly
- Validator runner produces correct count

**Gates passed:** LIF-6

---

## TC-VWR-008 — Pilot A: Single-Iteration Proof

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Gates:** LIF-12
**Depends:** TC-VWR-003, TC-VWR-004, TC-VWR-005, TC-VWR-006, TC-VWR-007
**Files owned:** `tests/supervisor/pilots/`

**Objective:** Prove that with Check B1 implemented, a machinery plan with all taskcards CLOSED
but 0 behavioral iterations returns AUDIT_REQUIRES_ITERATION (not AUDIT_PASS), then
generate_behavioral_gap_taskcards() creates a new taskcard, and after 1 iteration cycle
(behavioral_iterations_required=1 for pilot), AUDIT_PASS fires and TERMINAL_CLOSED is written.

### TC-VWR-008-01 — Create pilot-a plan file

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-008

**Micro-steps:**

MS-VWR-008-01-01
- Action: Create `tests/supervisor/pilots/pilot-a-single-iteration.md`:

```markdown
# pilot-a-single-iteration — Single Iteration Proof Plan

**plan_type:** machinery_hardening
**mission_id:** PILOT-A-001
**behavioral_iterations_required:** 1

## Taskcard Status Table

| Taskcard | Status |
|----------|--------|
| TC-PILOT-A-001 | OPEN |
| TC-PILOT-A-CLOSE | OPEN |

## TC-PILOT-A-001 — Execute trivial machinery change

Execute: write a timestamp to `tests/supervisor/pilots/pilot-a-artifact.txt`
Verify: file exists with current timestamp
Close this taskcard when done.

## TC-PILOT-A-CLOSE — Lifecycle audit gate
```

- Next: COMPLETE → close TC-VWR-008-01

---

### TC-VWR-008-02 — Create run_pilot_a.py script

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-008
**Depends:** TC-VWR-008-01

**Micro-steps:**

MS-VWR-008-02-01
- Action: Create `tests/supervisor/pilots/run_pilot_a.py`:

```python
"""
Pilot A: Single-Iteration Proof
Proves that Check B1 blocks AUDIT_PASS at iter=0 and allows it at iter=1.
"""
import json
import datetime
from pathlib import Path
import sys
import os

# Ensure repo root is on path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

MISSION_ID = "PILOT-A-001"
PLAN_PATH = str(REPO_ROOT / "tests" / "supervisor" / "pilots" / "pilot-a-single-iteration.md")
LEDGER_PATH = REPO_ROOT / ".local" / "supervisor" / "machinery" / "mission-ledger.json"


def write_ledger(iterations: int, required: int = 1) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps({
        "schema_version": "1.0",
        "mission_id": MISSION_ID,
        "mission_type": "machinery_hardening",
        "current_behavioral_iterations": iterations,
        "behavioral_iterations_required": required,
        "audit_pending": True,
        "stop_status": "RUNNING",
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")


def run():
    from tools.supervisor.lifecycle_audit import (
        run_lifecycle_audit,
        generate_behavioral_gap_taskcards,
        _increment_behavioral_iteration,
    )

    print("=== Pilot A: Step 1 — Set iter=0 in ledger ===")
    write_ledger(0)

    print("=== Pilot A: Step 2 — Run lifecycle_audit (all tasks CLOSED) ===")
    # Mark TC-PILOT-A-001 as CLOSED in plan file for the test
    plan_text = Path(PLAN_PATH).read_text(encoding="utf-8")
    plan_text = plan_text.replace("| TC-PILOT-A-001 | OPEN |", "| TC-PILOT-A-001 | CLOSED |")
    Path(PLAN_PATH).write_text(plan_text, encoding="utf-8")

    result = run_lifecycle_audit(
        mission_id=MISSION_ID,
        sprint_id="TC-PILOT-A-001",
        plan_path=PLAN_PATH,
    )
    print(f"Result: verdict={result['verdict']}, mission_complete={result['mission_complete']}")

    assert result["verdict"] == "AUDIT_REQUIRES_ITERATION", \
        f"FAIL: Expected AUDIT_REQUIRES_ITERATION at iter=0, got {result['verdict']}"
    print("PASS: AUDIT_REQUIRES_ITERATION returned at iter=0 (Check B1 working)")

    print("=== Pilot A: Step 3 — Generate behavioral gap taskcards ===")
    created = generate_behavioral_gap_taskcards(result["findings"], PLAN_PATH, MISSION_ID)
    assert len(created) >= 1, f"FAIL: Expected >=1 taskcard created, got {created}"
    print(f"PASS: {len(created)} behavioral gap taskcard(s) created: {created}")

    print("=== Pilot A: Step 4 — Increment behavioral iteration to 1 ===")
    write_ledger(1)

    print("=== Pilot A: Step 5 — Run lifecycle_audit again (iter=1 >= required=1) ===")
    # Mark new behavioral taskcard as CLOSED
    plan_text = Path(PLAN_PATH).read_text(encoding="utf-8")
    for tc_id in created:
        plan_text = plan_text.replace(f"| {tc_id} | OPEN |", f"| {tc_id} | CLOSED |")
    plan_text = plan_text.replace("| TC-PILOT-A-CLOSE | OPEN |", "| TC-PILOT-A-CLOSE | CLOSED |")
    Path(PLAN_PATH).write_text(plan_text, encoding="utf-8")

    result2 = run_lifecycle_audit(
        mission_id=MISSION_ID,
        sprint_id="TC-PILOT-A-CLOSE",
        plan_path=PLAN_PATH,
    )
    print(f"Result: verdict={result2['verdict']}, mission_complete={result2['mission_complete']}")

    assert result2["verdict"] == "AUDIT_PASS", \
        f"FAIL: Expected AUDIT_PASS at iter=1, got {result2['verdict']}"
    print("PASS: AUDIT_PASS at iter=1")
    print("=== Pilot A: ALL ASSERTIONS PASSED ===")
    return True


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
```

- Verify: file created, no syntax errors (read back)
- Next: COMPLETE → close TC-VWR-008-02

---

### TC-VWR-008-03 — Run Pilot A and record result

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-008
**Depends:** TC-VWR-008-02

**Micro-steps:**

MS-VWR-008-03-01
- Action: Run `python tests/supervisor/pilots/run_pilot_a.py` from repo root
- Expected output: "=== Pilot A: ALL ASSERTIONS PASSED ==="
- If fails: diagnose assertion failure; fix the implementation (TC-VWR-003, TC-VWR-005) before retrying
- Record output in §Pilot Results section of this plan
- Next: COMPLETE → close TC-VWR-008-03

**Parent acceptance criteria (TC-VWR-008):**
- All 3 children CLOSED
- Pilot A passes: AUDIT_REQUIRES_ITERATION at iter=0, AUDIT_PASS at iter=1
- Result recorded in plan

**Gates passed:** LIF-12

---

## TC-VWR-009 — Pilot H: Multi-Iteration (3 Audit-Execute Cycles)

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Gates:** LIF-13, LIF-14, LIF-16, LIF-17, LIF-18
**Depends:** TC-VWR-008

**Objective:** Prove 3 complete audit-execute-reaudit cycles, plus pilot variants for iteration limit,
interrupted recovery, and stable rerun idempotency.

### TC-VWR-009-01 — Create pilot-h plan file

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-009

**Micro-steps:**

MS-VWR-009-01-01
- Action: Create `tests/supervisor/pilots/pilot-h-multi-iteration.md`:

```markdown
# pilot-h-multi-iteration — Multi-Iteration Proof Plan

**plan_type:** machinery_hardening
**mission_id:** PILOT-H-001
**behavioral_iterations_required:** 3

## Taskcard Status Table

| Taskcard | Status |
|----------|--------|
| TC-PILOT-H-001 | OPEN |
| TC-PILOT-H-CLOSE | OPEN |

## TC-PILOT-H-001 — Initial execution task
Execute trivial work (write timestamp to pilot-h-artifact.txt).

## TC-PILOT-H-CLOSE — Final lifecycle audit gate
```

- Next: COMPLETE → close TC-VWR-009-01

---

### TC-VWR-009-02 — Create run_pilot_h.py (3-cycle proof)

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-009
**Depends:** TC-VWR-009-01

**Micro-steps:**

MS-VWR-009-02-01
- Action: Create `tests/supervisor/pilots/run_pilot_h.py` with:
  - Phase 1: Write ledger iter=0, close TC-PILOT-H-001, run lifecycle_audit → AUDIT_REQUIRES_ITERATION; generate taskcards; increment to iter=1
  - Phase 2: Close iter-1 taskcards, run lifecycle_audit → AUDIT_REQUIRES_ITERATION (iter=1 < 3); generate taskcards; increment to iter=2
  - Phase 3: Close iter-2 taskcards, run lifecycle_audit → AUDIT_REQUIRES_ITERATION (iter=2 < 3); increment to iter=3
  - Phase 4: Run lifecycle_audit → AUDIT_PASS (iter=3 >= 3)
  - Assert: TERMINAL_CLOSED NOT written before Phase 4
  - Assert: 3 total audit-execute cycles documented
  - Pilot E subset: Set max_iterations=2, verify G3X fires (does not allow AUDIT_PASS)
  - Pilot G subset: Write partial ledger (mid-iteration state), run lifecycle_audit, verify recovery
  - Pilot I subset: Run lifecycle_audit a second time after AUDIT_PASS, verify no new taskcards

- Write the full script with all phases and assertions
- Next: COMPLETE → close TC-VWR-009-02

---

### TC-VWR-009-03 — Run Pilot H and record result

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-009
**Depends:** TC-VWR-009-02

**Micro-steps:**

MS-VWR-009-03-01
- Action: Run `python tests/supervisor/pilots/run_pilot_h.py` from repo root
- Expected: all assertions pass (3 cycles, AUDIT_PASS at iter=3, no premature TERMINAL_CLOSED)
- If fails: diagnose; fix implementation before retrying (max 3 attempts per BLOCKER RULE)
- Record output in §Pilot Results
- Next: COMPLETE → close TC-VWR-009-03

---

### TC-VWR-009-04 — Run full pytest regression suite

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-009
**Depends:** TC-VWR-009-03

**Micro-steps:**

MS-VWR-009-04-01
- Action: Run `.venv/Scripts/pytest tests/supervisor/ -v --tb=short 2>&1 | tail -40`
- Expected: all tests pass or pre-existing failures only (no NEW failures introduced by this plan's changes)
- If new failure: trace to the specific function changed in TC-VWR-003/004/005/006/007 and fix
- Record: test count (pass/fail/skip) in §Pilot Results
- Next: COMPLETE → close TC-VWR-009-04

**Parent acceptance criteria (TC-VWR-009):**
- All 4 children CLOSED
- Pilot H: 3 audit-execute cycles proven, TERMINAL_CLOSED only after iter=3
- Pilot E subset: G3X fires at MAX_ITERATIONS with incomplete behavioral proof
- Pilot G subset: interrupted recovery works
- Pilot I subset: stable rerun is idempotent
- Full pytest regression passes with no new failures

**Gates passed:** LIF-13, LIF-14, LIF-16, LIF-17, LIF-18

---

## TC-VWR-010 — Stable-ID Artifacts and Idempotency Registry

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Gates:** LIF-15, LIF-16
**Depends:** TC-VWR-001
**Parallel-safe with:** TC-VWR-003 through TC-VWR-007

**Objective:** Create the idempotency artifacts directory so that future reruns of this prompt
can detect prior closures and avoid duplicating work.

### TC-VWR-010-01 — Create artifacts directory and stable-id-registry.yaml

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-010

**Micro-steps:**

MS-VWR-010-01-01
- Action: Create directory `plans/.claude/velvet-swinging-wreath-artifacts/`
- Next: MS-VWR-010-01-02

MS-VWR-010-01-02
- Action: Create `plans/.claude/velvet-swinging-wreath-artifacts/stable-id-registry.yaml`
  with the content from §Stable-ID Registry section above (copy the YAML block)
- Add `authoritative_plan: plans/.claude/velvet-swinging-wreath.md`
- Add `artifact_role: analysis_or_evidence_only`
- Add `execution_authority: false`
- Next: MS-VWR-010-01-03

MS-VWR-010-01-03
- Action: Create `plans/.claude/velvet-swinging-wreath-artifacts/prior-run-reconciliation.yaml`:

```yaml
authoritative_plan: plans/.claude/velvet-swinging-wreath.md
artifact_role: analysis_or_evidence_only
execution_authority: false
reconciliation_run: 1
prior_closed_taskcards: []
note: "Populated on subsequent reruns. First run has no prior state to reconcile."
```

- Next: MS-VWR-010-01-04

MS-VWR-010-01-04
- Action: Create `plans/.claude/velvet-swinging-wreath-artifacts/rerun-idempotency-verdict.md`:

```markdown
# Rerun Idempotency Verdict

authoritative_plan: plans/.claude/velvet-swinging-wreath.md
artifact_role: analysis_or_evidence_only
execution_authority: false

## Run 1 (2026-07-10)

**Verdict:** FIRST_RUN — no prior state to reconcile.
New gaps found: 6 root causes (RC-001 through RC-006)
Taskcards created: TC-VWR-001 through TC-VWR-CLOSE

## Subsequent Runs

On rerun, the execution agent must:
1. Read this file
2. Read stable-id-registry.yaml
3. Check which TC-VWR-* IDs are CLOSED in the Taskcard Status Table
4. Skip re-creating work items for CLOSED taskcards
5. Update this file with new run number and verdict
```

- Next: COMPLETE → close TC-VWR-010-01

---

### TC-VWR-010-02 — Write lifecycle_stable_id.py utility

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-010
**Depends:** TC-VWR-010-01

**Micro-steps:**

MS-VWR-010-02-01
- Action: Create `tools/supervisor/lifecycle_stable_id.py`:

```python
"""
lifecycle_stable_id.py — Stable-ID registry for machinery plan reruns.

On rerun: reads prior registry, finds which stable IDs are already closed,
skips re-creating taskcards for closed IDs.
"""
from pathlib import Path
import json


REGISTRY_PATH = Path("plans/.claude/velvet-swinging-wreath-artifacts/stable-id-registry.yaml")


def get_closed_taskcard_ids(plan_path: str) -> set[str]:
    """Return set of taskcard IDs that are CLOSED in the plan's status table."""
    plan_file = Path(plan_path)
    if not plan_file.exists():
        return set()
    closed = set()
    in_table = False
    for line in plan_file.read_text(encoding="utf-8").splitlines():
        if "| Taskcard | Status |" in line:
            in_table = True
            continue
        if in_table and line.startswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[1].upper() == "CLOSED":
                closed.add(parts[0])
        elif in_table and not line.startswith("|"):
            in_table = False
    return closed


def is_taskcard_closed(tc_id: str, plan_path: str) -> bool:
    return tc_id in get_closed_taskcard_ids(plan_path)


def report_idempotency(plan_path: str) -> dict:
    closed = get_closed_taskcard_ids(plan_path)
    return {
        "closed_count": len(closed),
        "closed_ids": sorted(closed),
        "verdict": "IDEMPOTENT_NO_CHANGE" if len(closed) > 0 else "FIRST_RUN",
    }


if __name__ == "__main__":
    import sys
    plan = sys.argv[1] if len(sys.argv) > 1 else "plans/.claude/velvet-swinging-wreath.md"
    report = report_idempotency(plan)
    print(json.dumps(report, indent=2))
```

- Next: MS-VWR-010-02-02

MS-VWR-010-02-02
- Action: Run `python tools/supervisor/lifecycle_stable_id.py plans/.claude/velvet-swinging-wreath.md`
- Expected: JSON output showing closed_count, closed_ids, verdict
- If ImportError or file not found: verify paths and fix
- Next: COMPLETE → close TC-VWR-010-02

**Parent acceptance criteria (TC-VWR-010):**
- Both children CLOSED
- Artifacts directory created with 3 files
- lifecycle_stable_id.py runs without error
- All artifact files marked `execution_authority: false`

**Gates passed:** LIF-15, LIF-16

---

## TC-VWR-011 — Execution Handoff and Final Report

**Type:** PARENT
**Status:** OPEN
**Lane:** machinery_governance
**Gates:** LIF-19, LIF-20
**Depends:** TC-VWR-009, TC-VWR-010

**Objective:** Write the complete execution handoff YAML and gate status table into this plan.
Write the evidence declaration for sprint closeout.

### TC-VWR-011-01 — Write gate status table to plan

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-011

**Micro-steps:**

MS-VWR-011-01-01
- Action: Update "## Gate Status Table" section in `plans/.claude/velvet-swinging-wreath.md`
  with actual PASS/FAIL/NOT_RUN classification for LIF-0 through LIF-20
- Base on actual pilot and validator results from TC-VWR-008 and TC-VWR-009
- Next: COMPLETE → close TC-VWR-011-01

---

### TC-VWR-011-02 — Write execution handoff YAML to plan

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-011

**Micro-steps:**

MS-VWR-011-02-01
- Action: Replace "## Execution Handoff" scaffold section with full YAML (see scaffold at plan bottom)
- Fill in: all runtime-discovered paths, commands, and mission state
- Next: COMPLETE → close TC-VWR-011-02

---

### TC-VWR-011-03 — Write evidence declaration

**Type:** CHILD
**Status:** TODO
**Parent:** TC-VWR-011

**Micro-steps:**

MS-VWR-011-03-01
- Action: Create directory `.local/evidences/vwr-20260710/`
- Next: MS-VWR-011-03-02

MS-VWR-011-03-02
- Action: Write `.local/evidences/vwr-20260710/evidence-declaration.yaml` with:
  - mission_id: VELVET-SWINGING-WREATH-001
  - worker_verdict: ACCEPTED (if all pilots pass) or ACCEPTED_WITH_REWORK
  - planned_work_items: list all TC-VWR-* with status and evidence paths
  - test_results: pytest counts from TC-VWR-009-04
  - pilot_results: pilot A and H pass/fail
  - changed_files: all files modified across TC-VWR-003 through TC-VWR-007 and TC-VWR-010
- Next: COMPLETE → close TC-VWR-011-03

**Parent acceptance criteria (TC-VWR-011):**
- All 3 children CLOSED
- Gate status table complete (LIF-0 through LIF-20 classified)
- Execution handoff YAML complete
- Evidence declaration written

**Gates passed:** LIF-19, LIF-20

---

## TC-VWR-CLOSE — Final Lifecycle Audit Gate and Plan Closure

**Type:** PARENT (terminal)
**Status:** OPEN
**Lane:** machinery_governance
**Depends:** ALL prior taskcards CLOSED

### Objective

Run the post-plan lifecycle audit, verify behavioral iteration count >= 2, and write terminal lock.

### Steps

1. Verify all TC-VWR-001 through TC-VWR-011 (and all children) show CLOSED in the Taskcard Status Table above
2. Verify `.local/supervisor/machinery/mission-ledger.json` shows `mission_id = "VELVET-SWINGING-WREATH-001"` and `current_behavioral_iterations >= 2`
3. Run:
   ```bash
   python tools/supervisor/lifecycle_audit.py \
     --mission-id VELVET-SWINGING-WREATH-001 \
     --sprint-id TC-VWR-011 \
     --plan-path plans/.claude/velvet-swinging-wreath.md
   ```
4. **If AUDIT_PASS:** run:
   ```bash
   python tools/supervisor/write_plan_lock.py \
     --plan-path plans/.claude/velvet-swinging-wreath.md \
     --terminal --audit-gate
   ```
   Then report: "Plan velvet-swinging-wreath complete. All N taskcards closed. Behavioral iterations: K. Lifecycle healing proven through K audit-execute cycles. Awaiting your next instruction."

5. **If AUDIT_REQUIRES_ITERATION:** new taskcards will be auto-generated by `generate_behavioral_gap_taskcards()`. Add them to the Taskcard Status Table and execute them before retrying TC-VWR-CLOSE.

---

## Verification Plan

### End-to-end test commands

```bash
# 1. Verify new functions exist in lifecycle_audit.py
python -c "from tools.supervisor.lifecycle_audit import _read_machinery_mission_ledger, _check_behavioral_iteration_guard, generate_behavioral_gap_taskcards, _increment_behavioral_iteration; print('All functions OK')"

# 2. Verify governance validators include new V_MACH_* validators
python tools/supervisor/governance_validator_runner.py 2>&1 | tail -5

# 3. Run Pilot A (single iteration proof)
python tests/supervisor/pilots/run_pilot_a.py

# 4. Run Pilot H (3-cycle multi-iteration proof)
python tests/supervisor/pilots/run_pilot_h.py

# 5. Run full supervisor test suite
.venv/Scripts/pytest tests/supervisor/ -v --tb=short 2>&1 | tail -20

# 6. Run lifecycle audit for this plan
python tools/supervisor/lifecycle_audit.py \
  --mission-id VELVET-SWINGING-WREATH-001 \
  --sprint-id TC-VWR-CLOSE \
  --plan-path plans/.claude/velvet-swinging-wreath.md
```

### Negative controls

| Scenario | Expected behavior |
|----------|-----------------|
| lifecycle_audit called on machinery plan with iter=0 | AUDIT_REQUIRES_ITERATION (not AUDIT_PASS) |
| G4 called with missing sprint-audit-log.json | CRITICAL finding (not graceful skip) |
| G3X: MAX_ITERATIONS + iter < required | CRITICAL finding (not AUDIT_PASS) |
| generate_behavioral_gap_taskcards called twice | Idempotent (no duplicates) |
| V_MACH_ITERATION_PROOF with TERMINAL_CLOSED + iter=0 | BLOCK finding |
| Non-machinery plan (plan_type: foss_python) | Check B1 does NOT fire |

---

## Evidence Contract

```yaml
evidence_root: .local/evidences/vwr-20260710/
authoritative_plan: plans/.claude/velvet-swinging-wreath.md
evidence_obligation_matrix:
  - taskcard: TC-VWR-003
    evidence: grep output confirming _check_behavioral_iteration_guard in lifecycle_audit.py
  - taskcard: TC-VWR-004
    evidence: .local/supervisor/machinery/mission-ledger.json with VELVET-SWINGING-WREATH-001 entry
  - taskcard: TC-VWR-005
    evidence: test_taskcard_generation.py pytest output (3 passed)
  - taskcard: TC-VWR-006
    evidence: test_lifecycle_guards.py pytest output
  - taskcard: TC-VWR-007
    evidence: governance_validator_runner.py output showing 170 validators
  - taskcard: TC-VWR-008
    evidence: run_pilot_a.py stdout ("ALL ASSERTIONS PASSED")
  - taskcard: TC-VWR-009
    evidence: run_pilot_h.py stdout (3 cycles proven) + full pytest output
  - taskcard: TC-VWR-010
    evidence: ls plans/.claude/velvet-swinging-wreath-artifacts/
  - taskcard: TC-VWR-011
    evidence: .local/evidences/vwr-20260710/evidence-declaration.yaml
```

---

## Remaining Known Risks

1. **`lifecycle_audit.py` function signature for G4:** The exact function name `check_sprint_audit_guard` and its parameter names need to be confirmed in MS-VWR-006-02-02. If the signature differs, the test must adapt.
2. **`run_lifecycle_audit()` variable names:** MS-VWR-003-04-01 must read the actual code to find `_plan_type` and `mission_id` variable names before wiring Check B1. These may differ from what's assumed.
3. **governance_validators_ext4.py registry pattern:** Some validator registries use lists, others dicts, others auto-discovery via function naming convention. MS-VWR-007-05-01 must read the actual pattern before adding entries.
4. **Pilot H script complexity:** TC-VWR-009-02 creates a non-trivial orchestration script. If lifecycle_audit's `run_lifecycle_audit()` has side effects (e.g., writes files), the pilot must use a temp directory to avoid polluting real state.
5. **expected_count discrepancy:** Adding 3 validators (V_MACH_CONTINUATION_CONSUMED deferred) brings count from 167 to 170. If any validators were added between the last count update (V149) and now, this number may differ. Always re-read the runner before updating.

---

## Pilot Results (to be filled during TC-VWR-008 and TC-VWR-009)

_Filled during execution._

---

## Gate Status Table (to be filled during TC-VWR-011)

_Gates LIF-0 through LIF-20 will be classified here after pilots complete._

---

## Execution Handoff (to be completed in TC-VWR-011)

```yaml
execution_handoff:
  mission_id: VELVET-SWINGING-WREATH-001
  authoritative_plan_path: plans/.claude/velvet-swinging-wreath.md
  plan_mode: EXISTING_AUTHORITATIVE_PLAN_REPAIR
  selected_controller: tools/supervisor/autonomous_cycle.py
  lifecycle_entry_point: "python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration <decl>"
  sprint_audit_entry_point: "python tools/supervisor/lifecycle_audit.py --mission-id VELVET-SWINGING-WREATH-001 --sprint-id <TC-ID> --plan-path plans/.claude/velvet-swinging-wreath.md"
  plan_hardening_entry_point: "Edit plans/.claude/velvet-swinging-wreath.md (add taskcards from audit findings)"
  taskcard_generation_entry_point: "generate_behavioral_gap_taskcards() — auto-called by write_plan_lock.py on ITERATION_REQUIRED"
  post_execution_audit_entry_point: "python tools/supervisor/lifecycle_audit.py --mission-id VELVET-SWINGING-WREATH-001"
  mission_completion_audit_entry_point: "python tools/supervisor/lifecycle_audit.py --mission-id VELVET-SWINGING-WREATH-001 --require-behavioral-iterations 2 (after TC-VWR-003 is implemented)"
  plan_closure_entry_point: "python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/velvet-swinging-wreath.md --terminal --audit-gate"
  taskcard_root: plans/.claude/velvet-swinging-wreath.md
  mission_state_root: .local/supervisor/machinery/mission-ledger.json
  evidence_root: .local/evidences/vwr-20260710/
  pilots_dir: tests/supervisor/pilots/
  allowed_stop_conditions:
    - MISSION_COMPLETE (after behavioral_iterations >= 2 proven through pilots)
    - BLOCKED_EXTERNAL (TRUE_EXTERNAL_GATE only)
  prohibited_stop_conditions:
    - TERMINAL_CLOSED before behavioral_iterations >= 2
    - MAX_ITERATIONS treated as completion (G3X guards against this)
    - Closeout task as terminal work (G2 guards against this)
    - Task closure without post-execution audit (Check B1 guards against this)
  final_evidence_bundle_required: true
  absolute_evidence_path_required: true
  absolute_evidence_path_prefix: "C:\\Users\\prora\\OneDrive\\Documents\\GitHub\\format-factory\\"
```

---

## Single-Plan Authority Confirmation

This document is the SOLE authoritative plan for VELVET-SWINGING-WREATH-001.

- No competing plan was created
- Supporting artifacts in `plans/.claude/velvet-swinging-wreath-artifacts/` are marked `execution_authority: false`
- All taskcards in this document trace to root causes RC-001 through RC-006
- All evidence artifacts reference this plan path
- The execution handoff points to exactly one plan path: `plans/.claude/velvet-swinging-wreath.md`
