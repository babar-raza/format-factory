# Lifecycle Truth Table — Machinery Iteration Forensics
# Run: machinery-lifecycle-forensics-20260621

| Lifecycle Stage | Defined | Invokable | Auto-Invoked | Consumed | Enforced | Tested | Status |
|-----------------|---------|-----------|--------------|----------|----------|--------|--------|
| Sprint audit (post-execution) | PARTIAL (archaeology did it once) | YES (as standalone sprint) | NO | NO | NO | NO | PRODUCER_ONLY |
| Gap extraction | YES (system-gap-matrix.yaml from archaeology) | YES (manual read) | NO | NO | NO | NO | PRODUCER_ONLY |
| Plan creation / update | YES (machinery-repair-plan.md in reports) | YES (file exists) | NO | NO | NO | NO | PRODUCER_ONLY |
| Plan hardening | NO (for machinery track) | NO | NO | NO | NO | NO | MISSING |
| Taskcard generation | PARTIAL (taskcards.yaml in archaeology report) | YES (file exists) | NO | NO | NO | NO | PRODUCER_ONLY |
| Execution | YES (autonomous_cycle.py + sprint_executor) | YES | NO (blocked by PLAN_COMPLETED_IN_SESSION) | N/A | N/A | YES | BLOCKED |
| Focused verification | YES (pytest) | YES | NO | NO | NO | YES | CONNECTED_BUT_OPTIONAL |
| Integration verification | PARTIAL (dogfood tests) | YES | NO | NO | NO | NO | CONNECTED_BUT_OPTIONAL |
| End-to-end verification | NO | NO | NO | NO | NO | NO | MISSING |
| Evidence reconciliation | YES (evidence declaration) | YES | NO | YES (autonomous_cycle reads it) | YES (schema validation) | YES | CONNECTED_AND_ENFORCED |
| Post-execution sprint audit | NO (for machinery) | NO | NO | NO | NO | NO | MISSING |
| Continuation decision | YES (check_continuation.py) | YES | YES (called by sprint loop) | YES (drives loop) | YES (hard stops) | YES | CONNECTED_AND_ENFORCED |
| Rework / replan | PARTIAL (rework_items in signal) | PARTIAL | NO | NO | PARTIAL | NO | PRODUCER_ONLY |
| Next execution iteration | YES (next-sprint.md) | YES (file read) | NO (blocked) | NO | NO | NO | BLOCKED |
| Mission completion audit | NO | NO | NO | NO | NO | NO | MISSING |
| Stop (mission-aware) | NO (only sprint-aware) | NO | N/A | N/A | N/A | NO | MISSING |

## Critical Findings

1. **Post-execution sprint audit**: MISSING — no stage exists to re-audit after executing repair tasks
2. **Plan hardening (machinery)**: MISSING — no hardening step for machinery plan
3. **Mission completion audit**: MISSING — no gate that distinguishes mission-complete from task-complete
4. **End-to-end verification**: MISSING — no stage to verify the full machinery lifecycle works
5. **Continuation is BLOCKED**: `check_continuation.py` returns PLAN_COMPLETED_IN_SESSION (NON-OVERRIDABLE)

## Workflow Enforcement Gaps

### GAP-WF-001: Investigation sprint has no execution consumer
- The archaeology produces `next-agent-execution-prompt.md` but no controller consumes it.
- Classification: PRODUCER_ONLY

### GAP-WF-002: Plan reopening has no mechanism
- After audit finds new gaps, no tool re-opens the authoritative plan with new taskcards.
- Classification: MISSING

### GAP-WF-003: Mission state is undefined
- There is no mission ledger distinguishing machinery mission state from sprint state.
- Classification: MISSING

### GAP-WF-004: Continuation blocker has no resolution path for machinery
- PLAN_COMPLETED_IN_SESSION is NON-OVERRIDABLE and has no self-clearing mechanism.
- To unblock: explicit user authorization OR creation of new per-chat plan for machinery.
- Classification: CONNECTED_BUT_OPTIONAL (requires human intervention)
