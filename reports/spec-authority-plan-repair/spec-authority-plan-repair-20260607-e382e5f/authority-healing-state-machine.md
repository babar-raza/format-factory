# Authority Healing State Machine
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# State count: 32
# Date: 2026-06-07

---

## State Count Declaration: 32

(REPAIR-001 applied: prior plan incorrectly stated 29 states; programmatic count = 32)

---

## States

### Non-Terminal States (29)

| State | Entry Criteria | Exit Criteria | Transitions To |
|-------|---------------|---------------|----------------|
| DISCOVERED | gap_id_assigned | evidence_source_identified | EVIDENCE_IMPORTED, BLOCKED_BY_MISSING_EVIDENCE |
| EVIDENCE_IMPORTED | evidence_files_read | gap_classification_complete | TRIAGED, BLOCKED_BY_MISSING_EVIDENCE |
| TRIAGED | gap_classification_complete | root_cause_written | ROOT_CAUSE_CONFIRMED |
| ROOT_CAUSE_CONFIRMED | root_cause_written | taskcard_written | TASKCARD_CREATED, BLOCKED_BY_MISSING_EVIDENCE |
| TASKCARD_CREATED | all_required_fields_present | prerequisites_unblocked | READY_FOR_DESIGN, BLOCKED_BY_PREREQUISITE_TASKCARD |
| BLOCKED_BY_MISSING_EVIDENCE | evidence_gap_identified | evidence_gap_resolved | EVIDENCE_IMPORTED, TRIAGED |
| BLOCKED_BY_MISSING_SPEC | spec_pdf_not_found | spec_pdf_present | READY_FOR_DESIGN |
| BLOCKED_BY_EXTERNAL_AUTHORITY | external_gate_required | external_gate_cleared | READY_FOR_DESIGN, RELEASE_GATE_ENFORCED |
| BLOCKED_BY_PREREQUISITE_TASKCARD | prerequisite_not_closed | prerequisite_closed | READY_FOR_DESIGN |
| READY_FOR_DESIGN | prerequisites_unblocked | design_document_written | DESIGN_COMPLETE |
| DESIGN_COMPLETE | design_document_written | implementation_scope_confirmed | READY_FOR_IMPLEMENTATION |
| READY_FOR_IMPLEMENTATION | scope_confirmed | implementation_started | IMPLEMENTING |
| IMPLEMENTING | implementation_started | artifacts_written | IMPLEMENTED |
| IMPLEMENTED | artifacts_written | validation_started | VALIDATING |
| VALIDATING | validation_started | gates_pass_or_fail | PILOT_READY, VALIDATION_FAILED, INDEPENDENT_VERIFICATION_REQUIRED |
| VALIDATION_FAILED | validation_gate_failed | fix_applied | IMPLEMENTING, BLOCKED_BY_MISSING_EVIDENCE |
| PILOT_READY | all_gates_pass, pilot_plan_written | pilot_started | PILOT_RUNNING, BLOCKED_BY_MISSING_SPEC |
| PILOT_RUNNING | pilot_started | pilot_complete | PILOT_PASSED, PILOT_FAILED |
| PILOT_FAILED | pilot_complete, result=fail | root_cause_identified | ROOT_CAUSE_CONFIRMED, BLOCKED_BY_MISSING_EVIDENCE |
| PILOT_PASSED | pilot_complete, result=pass | verification_scheduled | INDEPENDENT_VERIFICATION_REQUIRED, AUTHORITY_DEBT_RECORDED |
| INDEPENDENT_VERIFICATION_REQUIRED | verification_needed | review_complete | INDEPENDENT_VERIFIED, VALIDATION_FAILED |
| INDEPENDENT_VERIFIED | review_complete, no_critical_issues | closure_criteria_met | CLOSED_VERIFIED, SUPERVISOR_GATE_ENFORCED, PROOF_GRAPH_ENFORCED |
| HUMAN_APPROVAL_REQUIRED | external_authority_needed | human_decision_recorded | BLOCKED_BY_EXTERNAL_AUTHORITY, RELEASE_GATE_ENFORCED |
| AUTHORITY_DEBT_RECORDED | known_debt_documented | acknowledged | CLOSED_WITH_AUTHORITY_DEBT, DOWNGRADED_NON_PRODUCT |
| DOWNGRADED_NON_PRODUCT | reclassified | bypass_ledger_written | CLOSED_WITH_AUTHORITY_DEBT |
| SUPERVISOR_GATE_ENFORCED | supervisor_check_run | gate_passed | PROOF_GRAPH_ENFORCED, VALIDATION_FAILED |
| PROOF_GRAPH_ENFORCED | graph_edge_written | graph_valid | LEDGER_ENFORCED, VALIDATION_FAILED |
| LEDGER_ENFORCED | ledger_entry_written | ledger_valid | RELEASE_GATE_ENFORCED, VALIDATION_FAILED |
| RELEASE_GATE_ENFORCED | release_check_run | gate_passed_or_blocked | CLOSED_VERIFIED, BLOCKED_BY_EXTERNAL_AUTHORITY |

### Terminal States (3)

| State | Meaning |
|-------|---------|
| CLOSED_VERIFIED | All closure criteria met; evidence bundle present; fully verified |
| CLOSED_WITH_AUTHORITY_DEBT | Accepted with known debt documented in bypass ledger |
| REJECTED_FALSE_CLAIM | Claim found false or unverifiable; investigation required |

---

## Human Approval Required: Only for External Authority Decisions

States with `human_approval_required: true`:
- **BLOCKED_BY_EXTERNAL_AUTHORITY** — Gate 11, git push/commit, package publish, legal decisions
- **HUMAN_APPROVAL_REQUIRED** — Same scope as above

All other state transitions may be made by agent or supervisor roles.

`validated_by: independent_agent_verifier` is used for agent-verifiable facts.
`validated_by: human` is ONLY used when a human actually reviewed (e.g., Babar Raza Gate 11 approval).

---

## BLOCKED States (require evidence to unblock)

- BLOCKED_BY_MISSING_EVIDENCE — find the evidence
- BLOCKED_BY_MISSING_SPEC — acquire spec PDF (T3 authorized)
- BLOCKED_BY_EXTERNAL_AUTHORITY — Gate 11 or commit/push approval
- BLOCKED_BY_PREREQUISITE_TASKCARD — prerequisite taskcard must close first
- VALIDATION_FAILED — fix the defect
- PILOT_FAILED — investigate root cause

---

## Validation

```bash
python -m json.tool authority-healing-state-machine.json
python -c "import json; sm=json.load(open('authority-healing-state-machine.json')); n=len(sm['states']); assert n==32, f'Expected 32, got {n}'; print(f'OK: {n} states')"
```
