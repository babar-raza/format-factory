# Taskcard Schema
# Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-PLAN-REPAIR-FOR-SINGLE-GO-EXECUTION-001
# Run: spec-authority-plan-repair-20260607-e382e5f
# Date: 2026-06-07

---

## Required Fields

Every taskcard in authority-healing-taskcards.json must have all of the following fields:

| Field | Type | Description |
|-------|------|-------------|
| taskcard_id | string | Format TCA-NNN |
| title | string | Descriptive title |
| stream | string | Must be 'authority-healing' |
| lane | string | One of L-COORD, L-EVIDENCE, L-STATEMACHINE, L-GOVERNANCE, L-SCHEMA, L-SELECTOR, L-VERIFY, L-ADVERSARIAL, L-BUNDLE |
| root_cause_ids | array | GAP-xxx or BYP-xxx strings |
| evidence_source_ids | array | Investigation files or artifact paths |
| affected_pipeline_stages | array | Pipeline stages this taskcard repairs |
| affected_formats | array | Format IDs (e.g. fods, gnumeric) |
| current_state | string | Valid state_id from state machine |
| allowed_paths | array | Path patterns this taskcard may write to |
| forbidden_paths | array | Path patterns this taskcard must NOT write to |
| prerequisite_taskcards | array | TCA-xxx that must be CLOSED_VERIFIED before this starts |
| authority_inputs_required | array | Spec facts, requirements, or artifacts needed as input |
| authority_outputs_expected | array | Artifacts this taskcard produces |
| implementation_scope | string | Precise description of what this taskcard does |
| non_goals | array | Explicitly what this taskcard does NOT do |
| blocking_gates | array | Verification gates that block closure |
| validation_commands | array | Shell commands to verify output |
| negative_tests_required | array | Tests that must FAIL to confirm fix |
| pilot_required | boolean | Whether a pilot run is required |
| evidence_required | array | File paths this taskcard must produce |
| state_transition_rules | object | Maps conditions to state transitions |
| rollback_plan | string | What to do if this taskcard fails |
| risk_level | string | HIGH, MEDIUM, or LOW |
| owner_lane | string | Lane that owns this taskcard |
| independent_verifier_lane | string | Lane that independently verifies |
| final_state | string | Terminal or INDEPENDENT_VERIFIED state |
| closure_criteria | array | Specific conditions required for closure |

See taskcard-schema.json for machine-readable version.
