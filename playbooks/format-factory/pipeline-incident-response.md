<!--
playbook_contract:
  playbook_id: pipeline-incident-response
  title: "Respond to Pipeline Incident (Governance Validator Failure, GOV_BLOCK, Test Baseline Failure)"
  version: "1.0"
  status: ACTIVE
  category: sprint_task_template
  owner_layer: supervisor_governance
  authority: TASK_TEMPLATE
  purpose: >
    Structured response protocol for pipeline incidents: governance validator failures,
    GOV_BLOCK events, test baseline failures, and continuation signal blocks.
    Prevents wrong remediation (e.g., bypassing with --no-verify, marking false complete).
  applicability: >
    A governance validator has returned exit 3 or exit 1. A GOV_BLOCK event has occurred.
    Test baseline has failed. check_continuation.py returns unexpected STOP.
    autonomous-cycle.py reports rework_items.
  triggers:
    - GOV_BLOCK in rework_items from check_continuation.py
    - exit_code_3 from autonomous-cycle.py
    - test_baseline_failure in next-sprint.md
    - APPROVAL_GATE_NO for structural reasons
  prerequisites:
    - Access to rework_items JSON from check_continuation.py output
    - Access to latest evidence-declaration.yaml
    - Access to governance validator output
  required_inputs:
    - incident_type
    - failing_validator_or_test
    - rework_items_json
  optional_inputs:
    - sprint_id
    - declaration_path
  required_skills:
    - rollback-and-recovery
    - post-sprint-audit
  required_commands: []
  allowed_paths:
    - "tools/governance/"
    - "src/python/<format>/"
    - "tests/python/<format>/"
    - ".local/supervisor/"
    - ".local/evidences/<run-id>/"
    - "reports/supervisor/"
  forbidden_paths:
    - "--no-verify (git hook bypass)"
    - "registry/format-registry.yaml (no gate changes)"
    - "plans/strategic/"
    - "AGENTS.md"
    - "GOVERNANCE.md"
  phases:
    - classify_incident
    - identify_first_failing_boundary
    - determine_remediation
    - apply_remediation
    - verify_remediation
    - resume_pipeline
  task_types:
    - PIPELINE_INCIDENT_RESPONSE
    - GOV_BLOCK_REMEDIATION
    - TEST_BASELINE_REPAIR
  validation:
    - validator_passes_after_remediation: true
    - no_bypass_used: true
    - regression_test_added: true
  evidence_requirements:
    - incident_classification
    - first_failing_boundary
    - remediation_applied
    - validator_output_after_fix
    - regression_test_path
  rollback: >
    Revert source changes if remediation made things worse.
    Use rollback-and-recovery skill if needed.
    Re-run validators to confirm rollback successful.
    Document failed remediation attempt before trying alternative.
  stop_conditions:
    - incident_requires_structural_refactor_beyond_sprint_scope
    - true_external_gate_blocking_fix
    - remediation_makes_baseline_worse
  outputs:
    - incident_classification_report
    - remediation_summary
    - regression_test
    - pipeline_resume_confirmation
  supersedes: []
  limitations:
    - "No gate approval authority"
    - "No evidence contract replacement"
    - "Sprint task template only — responds to incidents, does not prevent them"
    - "GOV_BLOCK is NON-OVERRIDABLE by Supreme Directive — must resolve before product deepening"
-->

# Sprint Task Template: Pipeline Incident Response

**Skill ID**: pipeline-incident-response
**Version**: 1.0
**Authority**: Based on GOV_BLOCK handling rules in CLAUDE.md and AGENTS.md §AG1. Sprint Task Template.
**Category**: Sprint Task Template (see docs/governance/playbook-layer.md for acquisition playbooks)

---

## Purpose

Structured response protocol for pipeline incidents. Prevents wrong remediations (e.g.,
bypassing governance validators with --no-verify, marking work complete without fixing root cause).

---

## When to Use

- Governance validator returns exit 3 or reports GOV_BLOCK
- Test baseline failure blocks continuation
- check_continuation.py returns unexpected STOP with structural reason
- autonomous-cycle.py rework_items contains GOV_BLOCK validators

---

## Incident Classification

| Incident Type | Classification | Severity |
|---|---|---|
| GOV_BLOCK:monolith_detection_validator | STRUCTURAL — NON-OVERRIDABLE | P0 |
| GOV_BLOCK:validate_source_architecture | STRUCTURAL — NON-OVERRIDABLE | P0 |
| GOV_BLOCK:validate_multi_responsibility_file | STRUCTURAL — NON-OVERRIDABLE | P0 |
| GOV_BLOCK:validate_analytics_naming_enforced | STRUCTURAL — NON-OVERRIDABLE | P0 |
| exit_3 non-GOV_BLOCK | Non-blocking per Supreme Directive | P2 |
| test_baseline_failure | BLOCKING — fix before continuation | P1 |
| SESSION_MISMATCH | NON-OVERRIDABLE — cross-chat isolation | P0 |
| PLAN_COMPLETED_IN_SESSION | NON-OVERRIDABLE — terminal event | P0 |

---

## Response Protocol

### Step 1: Classify Incident
- Read rework_items from check_continuation.py JSON output
- Classify: GOV_BLOCK (P0) vs non-GOV_BLOCK exit 3 (P2) vs test failure (P1)
- **NEVER bypass --no-verify, NEVER skip governance validators**

### Step 2: Identify First Failing Boundary
- For GOV_BLOCK: identify which file in src/python/ violates the structural rule
- For test failure: identify which test and which function
- For exit 3: identify which rework items are real vs advisory

### Step 3: Determine Remediation

| Incident Type | Remediation |
|---|---|
| GOV_BLOCK:monolith_detection | Apply §8.1 Analytics Separation Protocol (production-library-standard-v2.md) |
| GOV_BLOCK:validate_source_architecture | Split file by responsibility; see /decompose-monolithic-codec |
| exit_3 non-blocking | Log and continue per Supreme Directive |
| test_baseline_failure | Fix test or fix source; run `.venv/Scripts/pytest` to verify |

### Step 4: Apply Remediation
- **GOV_BLOCK**: Run `/extract-analytics-from-monolith` or `/decompose-monolithic-codec`
- **Test failure**: Fix root cause; never skip tests with `-k not <test>`
- Log all changes in evidence

### Step 5: Verify Remediation
- Re-run governance validators: `python tools/supervisor/supervisor_loop.py autonomous-cycle --validate-only`
- Re-run tests: `.venv/Scripts/pytest tests/python/<format>/ -v`
- Confirm GOV_BLOCK is gone from rework_items
- Add regression test for the fixed case

### Step 6: Resume Pipeline
- Run check_continuation.py again
- Confirm verdict returns CONTINUE or legitimate STOP
- Proceed with next sprint

---

## Stop Conditions

| Condition | Action |
|-----------|--------|
| Structural refactor beyond sprint scope | Create gap + taskcard; descope to minimum fix |
| TRUE_EXTERNAL_GATE blocking fix | Classify and report; do not bypass |
| Remediation makes baseline worse | Rollback; document; try alternative approach |

---

## Known Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Using --no-verify to bypass pre-commit hooks | NEVER — investigate root cause instead |
| Marking GOV_BLOCK as "non-blocking" | GOV_BLOCK is NON-OVERRIDABLE — Supreme Directive does NOT apply |
| Skipping regression test after fix | Always add regression test — prevents recurrence |
| Fixing symptom not root cause | Always identify FIRST FAILING BOUNDARY, not just the test that fails |
| Treating SESSION_MISMATCH as a soft stop | NON-OVERRIDABLE — use reset_track_signal.py if intentional adoption |
