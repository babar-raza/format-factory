# Task Master — No-Drift State Contract

## Contract Statement

TM state is ALWAYS non-authoritative. It reflects and assists Format Factory work.
It does not define, control, or override Format Factory gates, evidence, or governance.

## The Six No-Drift Rules

### RULE-1: TM done does NOT mean FF gate closed

A TM task with `status: done` has no gate-closure authority.
Gate closure requires human approval at the Format Factory gate.

**Enforced by:** `validate_dual_orchestration_bridge.py` RULE-1

Violations:
- Task done + gate closure keyword in any task field
- Task done + `non_authoritative: false`

Allowed:
- Task done + `non_authoritative: true` + no gate closure keywords

### RULE-2: Ruflo complete does NOT mean evidence accepted

A Ruflo lane with `status: completed` does not mean the sprint evidence was accepted.
Evidence acceptance requires human IV review and gate approval.

**Enforced by:** `validate_dual_orchestration_bridge.py` RULE-2

### RULE-3: All Ruflo lanes must carry non_authoritative: true

Every lane in `next-ruflo-lanes.json` must have `non_authoritative: true`.
Absent or false values are contract violations.

**Enforced by:** `validate_dual_orchestration_bridge.py` RULE-3

### RULE-4: Ruflo state cannot claim gate closure

Ruflo lane fields must not contain gate closure keywords:
`gate_closed`, `gate_*_approved`, `commercial_product_ready`

**Enforced by:** `validate_dual_orchestration_bridge.py` RULE-4

### RULE-5: Supervisor verdict cannot claim gate approval

The supervisor verdict value must not be one of the forbidden patterns:
`GATE_APPROVED`, `COMMERCIAL_READY`, `PRODUCT_READY`, `RELEASE_AUTHORIZED`

Allowed supervisor verdicts (from schema):
- `SUPERVISOR_E2E_ACCEPTED_MODE3_DRYRUN_READY_MCP_APPROVAL_BLOCKED`
- `SUPERVISOR_E2E_ACCEPTED_WITH_LIMITATIONS`
- `SUPERVISOR_E2E_BLOCKED_NO_REAL_EVIDENCE_BUNDLE`
- `SUPERVISOR_E2E_BLOCKED_BY_REPO_CONFLICT`
- `SUPERVISOR_E2E_BLOCKED_BY_VALIDATION`
- `SUPERVISOR_E2E_REJECTED_UNSAFE_STATE`
- `SUPERVISOR_FOUNDATION_COMPLETE_READY_FOR_REPLAY`
- `SUPERVISOR_REPLAY_COMPLETE_READY_FOR_TM_RUFLO_DRYRUN`
- `PLAN_HEALED_READY_FOR_SINGLE_GO_EXECUTION_HANDOFF`
- `DUAL_ORCHESTRATION_SUPERVISOR_FOUNDATION_COMPLETE_READY_FOR_TM_RUFLO_DRY_RUN`

**Enforced by:** `validate_dual_orchestration_bridge.py` RULE-5

### RULE-6: TM state reverts on evidence failure

If `evidence-review.json` shows `fail_count > 0` and a TM task is `done`,
the task status must revert to `evidence_blocked`.

This prevents TM from advancing tasks past failed evidence.

**Enforced by:** `compare_goal_to_evidence.py` (contradiction: CRITICAL)

## Enforcement Chain

```
evidence-review.json
       │
       ▼
compare_goal_to_evidence.py          ← detects contradictions
       │
       ▼
contradictions.json
       │
       ▼
generate_supervisor_packet.py        ← generates repair sprint if contradictions
       │
       ▼
next-sprint-taskmaster.json          ← tasks reflect reality
       │
       ▼
validate_taskmaster_bridge.py        ← validates bridge refs
validate_dual_orchestration_bridge.py ← validates no-drift contract
```

## Gate Closure Keywords (Forbidden in TM/Ruflo State)

The following keywords must NOT appear in TM task fields or Ruflo lane fields:
- `gate_closed`
- `gate_11_approved` (or any gate_N_approved)
- `commercial_product_ready`
- `g11_g` combined with approval language
- `GATE_APPROVED`
- `COMMERCIAL_READY`
- `PRODUCT_READY`
- `RELEASE_AUTHORIZED`

These keywords are only valid in Format Factory evidence artifacts produced by validators.

## Consequences of Drift

If drift is detected by `validate_dual_orchestration_bridge.py`:
- `result.has_drift == True`
- `result.violations` lists each rule violated
- Supervisor generates repair-focused sprint (not advancement sprint)
- Human notified for CRITICAL drift
- TM state must be corrected before advancement resumes
