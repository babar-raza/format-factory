<!--
playbook_contract:
  playbook_id: audit-healing-sprint
  title: "Structured Audit-Find-Heal-Verify Sprint Cycle"
  version: "1.0"
  status: ACTIVE
  category: sprint_task_template
  owner_layer: supervisor_governance
  authority: TASK_TEMPLATE
  purpose: >
    Standardize the recurring audit-find-heal-verify sprint cycle used to resolve
    accumulated drift, stale state, policy violations, and GOV_BLOCK events.
    Prevents common failure mode: claiming audit complete without executing repairs,
    or executing repairs without re-verifying.
  applicability: >
    Accumulated drift detected. Multiple GOV_BLOCK events. Stale policy documents found.
    Coverage gaps identified. System healing required before product deepening can resume.
  triggers:
    - detect-stale-layer-state finds stale items
    - GOV_BLOCK accumulated across multiple sprints
    - post-sprint-audit finds partially_done or claimed_unproven items
    - Coverage universe report shows HIGH_VALUE_RECURRING_WORKFLOWS_WITHOUT_DISPOSITION > 0
  prerequisites:
    - Access to audit findings (from post-sprint-audit, detect-stale-layer-state, or equivalent)
    - All true external gates are documented (not claiming "needs human" without classification)
    - Sprint authorization for healing work
  required_inputs:
    - audit_source
    - findings_list
    - healing_scope
  optional_inputs:
    - sprint_id
    - priority_filter
  required_skills:
    - post-sprint-audit
    - plan-hardening
    - detect-stale-layer-state
    - rollback-and-recovery
  required_commands: []
  allowed_paths:
    - "tools/"
    - "tests/"
    - "reports/"
    - ".local/evidences/<run-id>/"
    - "plans/.claude/"
    - "playbooks/"
  forbidden_paths:
    - "src/net/ (no commercial source during healing)"
    - "registry/format-registry.yaml (no gate changes)"
    - "plans/strategic/ (no strategic plan changes without authority)"
    - "--no-verify"
  phases:
    - audit_all_findings
    - classify_findings
    - create_gap_entries
    - convert_gaps_to_taskcards
    - execute_repairs_in_priority_order
    - verify_each_repair
    - run_coverage_report
    - close_resolved_gaps
    - run_second_pass_verification
  task_types:
    - AUDIT_HEALING_SPRINT
    - STALE_STATE_REMEDIATION
    - GAP_CLOSURE
  validation:
    - all_p0_findings_resolved: true
    - governance_validators_pass_after_healing: true
    - no_new_violations_introduced: true
    - second_pass_zero_material_changes: true
  evidence_requirements:
    - audit_findings_report
    - gap_entries_created
    - taskcards_generated
    - repair_evidence_per_finding
    - verification_output_per_repair
    - second_pass_idempotency_report
  rollback: >
    Each repair is independently rollback-able. If a repair introduces regressions:
    revert that specific change, document failure mode, try alternative approach.
    Do NOT roll back all healing work if one repair fails — isolate and fix.
  stop_conditions:
    - repair_requires_spec_authority_decision
    - true_external_gate_required
    - repair_introduces_new_violations
  outputs:
    - audit_findings_report
    - closed_gap_list
    - healing_summary
    - verification_report
    - idempotency_confirmation
  supersedes: []
  limitations:
    - "No gate approval authority"
    - "No evidence contract replacement"
    - "Sprint task template only"
    - "Healing scope must be bounded — do not attempt global healing in one sprint"
    - "P0 (structural) findings MUST be resolved before product deepening resumes"
-->

# Sprint Task Template: Audit-Healing Sprint

**Skill ID**: audit-healing-sprint
**Version**: 1.0
**Authority**: Based on plan-hardening and post-sprint-audit skill patterns. Sprint Task Template.
**Category**: Sprint Task Template (see docs/governance/playbook-layer.md for acquisition playbooks)

---

## Purpose

Standardize the recurring audit-find-heal-verify sprint cycle. Prevents the common failure
mode of claiming audit complete without executing repairs, or executing repairs without
re-verifying. Ensures ALL material findings enter the canonical gap system.

---

## When to Use

- Accumulated drift detected by detect-stale-layer-state
- Multiple GOV_BLOCK events have occurred
- post-sprint-audit finds partially_done, claimed_unproven, or risk_not_reduced items
- Coverage universe report shows unresolved high-value gaps
- Policy documents are stale (discovered by inventory or consumer graph analysis)

---

## Audit Classification Categories

| Category | Description | Priority |
|---|---|---|
| completed_verified | Implemented AND verified with real tests | — |
| completed_but_weakly_verified | Proof is synthetic, narrow, or limited | P2 |
| partially_done | Code exists but unwired, unregistered, or unvalidated | P1 |
| not_attempted | Required work not started | P1 |
| claimed_unproven | Claimed completion without adequate proof | P0 |
| risk_not_reduced | Code changed but risk unchanged | P1 |
| stale_policy | Policy document contradicts code reality | P1 |

---

## Sprint Phases

### Phase 1: Audit All Findings
- Run `/post-sprint-audit` on recent sprint work
- Run `/detect-stale-layer-state` on all active layers
- Run coverage universe analysis if applicable
- Collect ALL findings into `findings_list`

### Phase 2: Classify Findings
- Assign priority (P0/P1/P2) using table above
- Identify first-failing-boundary for each finding
- Group by category (structural P0 first, then P1, then P2)

### Phase 3: Create Gap Entries
- Every material finding → gap entry in canonical gap system
- Use gap categories from plan template §19
- Assign owner and target resolution sprint
- **MATERIAL_PLAYBOOK_FINDINGS_WITHOUT_GAPS must = 0**

### Phase 4: Convert Gaps to Taskcards
- Every READY gap → bounded taskcard with clear verification criteria
- Taskcards must have: plan_id, gap_id, allowed_paths, validation, evidence_root, rollback
- **READY_PLAYBOOK_GAPS_WITHOUT_TASKCARDS must = 0**

### Phase 5: Execute Repairs (Priority Order)
- P0 first: claimed_unproven, structural GOV_BLOCK
- P1 next: partially_done, not_attempted, risk_not_reduced, stale_policy
- P2 last: completed_but_weakly_verified

### Phase 6: Verify Each Repair
- After each repair: run validators, run tests
- Confirm governance_validators_pass for changed files
- Add regression test for any test-related repair
- **Never claim repair complete without running validators**

### Phase 7: Run Coverage Report
- Re-run coverage universe analysis
- Confirm HIGH_VALUE_RECURRING_WORKFLOWS_WITHOUT_DISPOSITION = 0
- Update playbook-coverage-universe.yaml

### Phase 8: Close Resolved Gaps
- Mark gap entries as CLOSED with evidence references
- Update taskcard status to CLOSED
- Update plan taskcard status table

### Phase 9: Second-Pass Verification
- Re-run all validators on healed files
- Re-run test suite for changed areas
- Confirm zero material changes in second pass
- **MATERIAL_SECOND_RUN_CHANGES must = 0**

---

## Known Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Claiming audit complete after Phase 1 | Audit is a PHASE, not a terminal action — continue to execution |
| Healing by updating policy without fixing code | Fix root cause in code; update policy to match reality |
| Skipping Phase 9 second-pass verification | Always re-run — healing often has side effects |
| Creating gap entries without taskcards | Every READY gap must have a taskcard |
| Treating P0 findings as deferrable | P0 findings block product deepening per GOV_BLOCK rules |
| Running repairs in wrong order | Always P0 → P1 → P2; structural first |
