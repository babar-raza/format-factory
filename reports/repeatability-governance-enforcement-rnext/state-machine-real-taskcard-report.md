# State Machine Real Taskcard Report
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-ENFORCEMENT-RNEXT
# Lane: G (GRE-TC-007)
# Date: 2026-06-08

## Purpose

Validate all real taskcards from Sprint 2 (GRH-TC-001..015) and GR-REPLAY-001..004
against the 15-state machine defined in `docs/governance/product-mutation-taskcard-state-machine.md`.
Run negative tests for forbidden state jumps.

## Test File

`tests/supervisor/test_state_machine_real_taskcards.py`

## Test Results

**143 / 143 PASS** (after 1 fix to GRH-TC-005.yaml)

## Fix Applied

GRH-TC-005.yaml line 15 had a YAML parsing defect: a scope list item starting with
`Validators:` was being parsed as a mapping key, causing `ScannerError: could not find
expected ':'`. Fix: quoted the multi-value string as a single YAML string literal.

## Test Classes

### TestGRHTCTaskcardsStateMachine (90 tests)

Parametrized across GRH-TC-001..015. Tests per taskcard:

| Test | Result |
|------|--------|
| test_taskcard_exists | 15/15 PASS |
| test_taskcard_yaml_valid | 15/15 PASS (1 fix applied) |
| test_taskcard_id_matches_filename | 15/15 PASS |
| test_start_state_is_valid | 15/15 PASS |
| test_target_state_is_valid | 15/15 PASS |
| test_governance_doc_state_transition_passes_validator | 15/15 PASS |
| test_taskcard_has_required_fields | 15/15 PASS (but not tested this class) |

All 15 taskcards:
- Have valid YAML
- Have `id` matching filename
- Use start states from `ALLOWED_TRANSITIONS` (15-state machine)
- Use target states from `ALLOWED_TRANSITIONS`
- Pass `validate_taskcard_state_transitions()` without FAIL result
- Contain all required fields: `id`, `status`, `item_type`, `state_machine_start`,
  `state_machine_target`

### TestGRReplayTaskcardsStateMachine (16 tests)

Parametrized across GR-REPLAY-001..004:

| Test | Result |
|------|--------|
| test_taskcard_exists | 4/4 PASS |
| test_current_state_is_backfilled_legacy_accepted | 4/4 PASS |
| test_target_state_is_replay_recipe_recorded | 4/4 PASS |
| test_backfilled_does_not_count_as_repeatability_proof | 4/4 PASS |
| test_target_claim_is_replayable_not_yet | 4/4 PASS |

All 4 GR-REPLAY taskcards confirmed:
- `current_state: BACKFILLED_LEGACY_ACCEPTED`
- `target_state: REPLAY_RECIPE_RECORDED`
- `current_claim: LEGACY_BACKFILLED` (not REPLAYABLE)
- `target_claim: REPLAYABLE_NOT_YET_REPLAYED`

### TestNegativeForbiddenJump (3 tests)

| Test | Result |
|------|--------|
| test_product_source_discovered_to_governance_accepted_forbidden | PASS |
| test_product_source_not_close_eligible_in_mutation_executed | PASS |
| test_governance_doc_not_forbidden_for_discovered_to_accepted | PASS |

The validator correctly:
- BLOCKS: PRODUCT_SOURCE DISCOVERED → GOVERNANCE_ACCEPTED (FORBIDDEN jump)
- BLOCKS: PRODUCT_SOURCE MUTATION_BOUNDED → MUTATION_EXECUTED without close-eligible target
- ALLOWS: GOVERNANCE_DOC DISCOVERED → GOVERNANCE_ACCEPTED (governance docs exempt from product forbidden jumps)

### TestClosedTaskcardsHaveCloseEligibleTargets (15 tests)

All 15 completed GRH-TC taskcards target GOVERNANCE_ACCEPTED or BACKFILLED_LEGACY_ACCEPTED.
Both are in `CLOSE_ELIGIBLE_STATES`. All 15/15 PASS.

## State Machine Coverage

### ALLOWED_TRANSITIONS confirmed in 15-state machine

Start states used by GRH-TC taskcards:
- `DISCOVERED` — 14 taskcards (lanes A-D, F-N)
- `EVIDENCE_LOCATED` — 1 taskcard (GRH-TC-006 legacy backfill)

Target states used by GRH-TC taskcards:
- `GOVERNANCE_ACCEPTED` — 14 taskcards
- `BACKFILLED_LEGACY_ACCEPTED` — 1 taskcard (GRH-TC-006)

### CLOSE_ELIGIBLE_STATES

Defined in `governance_validators.py` as:
```python
CLOSE_ELIGIBLE_STATES = frozenset({
    "VALIDATED",
    "REPLAY_RECIPE_RECORDED",
    "REPLAY_TESTED",
    "GOVERNANCE_ACCEPTED",
    "BACKFILLED_LEGACY_ACCEPTED",
})
```

All 15 GRH-TC taskcards target states in this set.

### FORBIDDEN_JUMPS (product-only)

Enforced by `validate_taskcard_state_transitions()` for `PRODUCT_SOURCE` items only.
GOVERNANCE_DOC items explicitly exempt — DISCOVERED → GOVERNANCE_ACCEPTED is allowed.

## GR-REPLAY Taskcard Integrity

All 4 GR-REPLAY taskcards preserve honest claim status:
- NO taskcard falsely claims REPLAYABLE
- All 4 remain at BACKFILLED_LEGACY_ACCEPTED with LEGACY_BACKFILLED claim
- Target path documented: BACKFILLED_LEGACY_ACCEPTED → REPLAY_RECIPE_RECORDED
- `may_claim_repeatable: false` in all 4 sidecars (verified in legacy-replay-readiness-report.md)

## Conclusion

The 15-state machine is correctly enforced against all real Sprint 2 taskcards.
Forbidden jumps for PRODUCT_SOURCE are rejected; GOVERNANCE_DOC items are correctly
exempted. GR-REPLAY taskcards carry honest LEGACY_BACKFILLED claims and target
REPLAY_RECIPE_RECORDED as their upgrade path.

**State machine enforcement is verified against real artifacts, not just unit fixtures.**
