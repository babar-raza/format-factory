---
espanso_provenance:
  source_trigger: ":ff-machinery-iteration-forensics"
  source_block: 60
  source_line_range: [75371, 76974]
  gap_id: GAP-ESP-004
  extraction_date: "2026-07-03"
  capability_id: machinery-iteration-forensics
prompt_id: ESP-PROMPT-5
title: "Machinery Lifecycle Iteration Forensics"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Machinery Execution-Lifecycle Iteration Forensics

## Problem This Solves

A machinery plan was executed. The governing workflow should have triggered multiple
AUDIT → PLAN → EXECUTE → RE-AUDIT iterations. It did not. Execution stopped after one pass.

This protocol diagnoses WHY the iteration did not happen and repairs the machinery.

## Short-Context View

A machinery plan executed once but did not iterate. Investigate:
1. Was the continuation signal correct after closeout?
2. Did lifecycle_audit.py run and produce ITERATION_REQUIRED?
3. Did write_plan_lock.py use --terminal instead of --audit-gate?
4. Did check_continuation.py return STOP for an incorrect reason?
5. Were new taskcards created after the first audit pass?
Fix the machinery root cause, not the symptom.

---

## Required Lifecycle (the standard that was NOT followed)

```
SPRINT AUDIT
→ GAP ANALYSIS
→ PLAN OR PLAN EXPANSION
→ PLAN HARDENING
→ EXECUTION
→ VERIFICATION
→ SPRINT AUDIT AGAIN
→ NEW GAP ANALYSIS
→ PLAN UPDATE OR EXPANSION
→ NEXT EXECUTION ITERATION
→ REPEAT UNTIL TRUE COMPLETION
```

A machinery sprint is complete ONLY when:
1. The implementation is audited after execution
2. The audit verifies whether the intended behavior actually changed
3. Newly exposed gaps are captured
4. The authoritative plan is updated or expanded
5. New taskcards are created or reopened
6. The next execution iteration is actually consumed
7. The cycle continues until the audit finds no unresolved in-scope gaps

## Forensics Protocol

### Phase 1: State Reconstruction
```
→ Read .local/supervisor/continuation-signal.json
  → Was autonomous_continue set to true or false?
  → What was the iteration count? Did it hit max_iterations?

→ Read .local/supervisor/active-plan-lock.json
  → What is the status? (IN_PROGRESS / COMPLETE / TERMINAL_CLOSED / ITERATION_REQUIRED?)
  → Was --terminal used when --audit-gate was required?
  → Was --complete used instead of --terminal for a machinery plan?

→ Read .local/supervisor/lifecycle-audit-results.json (if it exists)
  → Was it produced? What verdict did it return?
  → Did it return ITERATION_REQUIRED or TERMINAL_CLOSED?

→ Read reports/supervisor/approval-gates.md
  → What was AUTONOMOUS_CONTINUE?
  → Were any contradictions blocking?

→ Read the plan file itself
  → Were all taskcards CLOSED when the loop stopped?
  → Were there open taskcards that were silently skipped?
```

### Phase 2: Root Cause Classification

Classify the failure into one of these categories:

| Category | Symptom | Root Cause |
|---|---|---|
| `WRONG_LOCK_FLAG` | Loop stopped after one pass | `--terminal` used instead of `--audit-gate` in a machinery plan |
| `AUDIT_NOT_RUN` | lifecycle_audit.py never called | Post-closeout step skipped |
| `AUDIT_PASSED_INCORRECTLY` | lifecycle_audit.py returned TERMINAL_CLOSED | Audit criteria too loose; open gaps not detected |
| `CONTINUATION_BLOCKED` | check_continuation.py returned STOP | SESSION_MISMATCH, MAX_ITERATIONS, or PLAN_COMPLETED_IN_SESSION |
| `TASKCARDS_NOT_EXPANDED` | Plan not updated after first audit | Agent marked plan COMPLETE without expanding new taskcards |
| `STOP_OVERRIDE_MISSING` | Non-terminal STOP consumed as terminal | Agent treated advisory STOP as a hard stop |
| `CONTEXT_EXHAUSTED` | Session ended mid-loop | Context limit reached, no handoff written |

### Phase 3: Repair

For each root cause:

**WRONG_LOCK_FLAG:**
```bash
python tools/supervisor/write_plan_lock.py \
  --plan-path <plan-path> --audit-gate
```
Then run lifecycle_audit.py and respond to its output.

**AUDIT_NOT_RUN:**
```bash
python tools/supervisor/lifecycle_audit.py \
  --mission-id <mission-id> --sprint-id <last-taskcard-id>
```
If ITERATION_REQUIRED: read .local/supervisor/lifecycle-audit-results.json,
add new taskcards to the plan, execute them.

**CONTINUATION_BLOCKED by MAX_ITERATIONS:**
```bash
# Reset iteration counter
python -c "
import json
f = '.local/supervisor/continuation-signal.json'
s = json.load(open(f))
s['iteration'] = 0
json.dump(s, open(f,'w'), indent=2)
"
```

**CONTINUATION_BLOCKED by SESSION_MISMATCH:**
```bash
python tools/supervisor/reset_track_signal.py --track product
```

**TASKCARDS_NOT_EXPANDED:**
- Run the lifecycle audit
- Read the audit findings
- Add new taskcards to the plan file
- Execute them immediately

### Phase 4: Prove Repair

After applying the fix:
1. Run `python tools/supervisor/check_continuation.py` — must return CONTINUE
2. Execute one more taskcard from the expanded plan
3. Run the lifecycle audit again
4. Confirm the loop iterates at least one more time

### Evidence Requirements
- Capture the original continuation-signal.json state
- Document which root cause category applies
- Show the repair command used
- Show that check_continuation.py returns CONTINUE after repair
- Show at least one additional taskcard executed after the repair

### Completion Gate
- Root cause identified and documented
- Repair applied and verified
- check_continuation.py returns CONTINUE (not STOP)
- Machinery plan has completed at least one additional iteration post-repair
