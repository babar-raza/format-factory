# Pipeline Enforcement Pilot Results
# Sprint: FORMAT-FACTORY-GOVERNANCE-REPEATABILITY-ENFORCEMENT-RNEXT
# Lane: K (GRE-TC-011)
# Date: 2026-06-08

## Core Question Answered

**Can the pipeline now block a false product-source repeatability claim?**

**YES.** 8 pilots run through `run_all_governance_validators()` (the function wired into
`autonomous_cycle.py` Step 2e). 4 negative pilots (false/invalid claims) all FAIL and
block the sprint. 4 positive pilots (honest claims) all PASS.

## Test Results

**30 / 30 PASS**

Test file: `tests/supervisor/test_pipeline_enforcement_pilots.py`
Log: `reports/repeatability-governance-enforcement-rnext/raw-logs/pilot-tests.log`

## Pilot Details

### ENF-PILOT-001: False REPLAYABLE claim without replay_recipe_path
- **Expected**: FAIL
- **Result**: FAIL (Validator 4: replay_recipe_required_validator)
- **Mechanism**: `claim_classification=REPLAYABLE_NOT_YET_REPLAYED` without
  `replay_recipe_path` triggers FAIL with `blocks_sprint=True`
- **Tests**: 4/4 PASS

### ENF-PILOT-002: PRODUCT_SOURCE missing execution_method
- **Expected**: FAIL
- **Result**: FAIL (Validator 1: execution_method_required_validator)
- **Mechanism**: PRODUCT_SOURCE item with no `execution_method` field → FAIL
- **Tests**: 3/3 PASS

### ENF-PILOT-003: Forbidden state jump DISCOVERED→GOVERNANCE_ACCEPTED (PRODUCT_SOURCE)
- **Expected**: FAIL
- **Result**: FAIL (Validator 10: taskcard_state_transition_validator)
- **Mechanism**: `state_machine_start=DISCOVERED`, `state_machine_target=GOVERNANCE_ACCEPTED`
  for `PRODUCT_SOURCE` item → FAIL with "FORBIDDEN" in issue text
- **Tests**: 4/4 PASS

### ENF-PILOT-004: MANUAL_UNGOVERNED with non-legacy claim
- **Expected**: FAIL
- **Result**: FAIL (Validator 7: manual_ungoverned_rejection_validator)
- **Mechanism**: `MANUAL_UNGOVERNED` with `GOVERNED_BUT_NOT_REPLAYED` claim
  (not `LEGACY_BACKFILLED`) → FAIL
- **Tests**: 3/3 PASS

### ENF-PILOT-005: Governance-only sprint
- **Expected**: PASS
- **Result**: PASS (all 10 validators pass, blocks_sprint=False)
- **Mechanism**: All items are GOVERNANCE_DOC/GOVERNANCE_SCHEMA with
  `exception_classification: investigation_only` → no product enforcement applied
- **Tests**: 4/4 PASS

### ENF-PILOT-006: Legacy backfill properly formed
- **Expected**: PASS
- **Result**: PASS (all 10 validators pass, blocks_sprint=False)
- **Mechanism**: `BACKFILLED_LEGACY_EXECUTION` + `LEGACY_BACKFILLED` claim +
  valid `idempotency_key` + sidecar present → all validators PASS
- **Tests**: 4/4 PASS

### ENF-PILOT-007: Mixed sprint — governance doc OK, product item bad
- **Expected**: FAIL (due to product item)
- **Result**: FAIL (Validator 4: product item missing replay_recipe_path)
- **Mechanism**: One governance doc passes all validators; one PRODUCT_SOURCE
  claiming REPLAYABLE without replay_recipe_path → overall FAIL
- **Tests**: 4/4 PASS (including verification that governance doc passes
  execution_method validator, only product item fails replay_recipe validator)

### ENF-PILOT-008: GOVERNED_BUT_NOT_REPLAYED (honest claim)
- **Expected**: PASS
- **Result**: PASS (all 10 validators pass, blocks_sprint=False)
- **Fix applied**: Initial fixture was missing `skill_id`, `skill_transcript_path`,
  `source_diff_paths` required for `MANUAL_GOVERNED_BY_SKILL` method. Added these
  fields to the fixture. The `replay_recipe_required_validator` does NOT block
  `GOVERNED_BUT_NOT_REPLAYED` (only blocks `REPLAYABLE_*` claims without recipe).
- **Tests**: 4/4 PASS

## Key Enforcement Properties Verified

| Property | Verified By |
|----------|-------------|
| False REPLAYABLE claim blocked | ENF-PILOT-001, ENF-PILOT-007 |
| Missing execution_method blocked | ENF-PILOT-002 |
| Forbidden state jump blocked | ENF-PILOT-003 |
| MANUAL_UNGOVERNED with bad claim blocked | ENF-PILOT-004 |
| Governance docs exempt from product rules | ENF-PILOT-005 |
| Legacy backfill accepted | ENF-PILOT-006 |
| Honest governed claim accepted | ENF-PILOT-008 |
| One bad item in mixed sprint blocks overall | ENF-PILOT-007 |

## Pipeline Path Confirmed

The enforcement path for blocking false claims is:

```
evidence-declaration.yaml
  → autonomous_cycle.py Step 2e
    → run_all_governance_validators(decl, repo_root)
      → 10 individual validators
    → governance-validation-result.json written to review dir
    → if blocks_sprint=True: overall_verdict downgraded to ACCEPTED_WITH_REWORK
```

This was verified in `tests/supervisor/test_pipeline_governance_wiring.py` (11 tests)
and confirmed working end-to-end by these 8 enforcement pilots.

## False Claim Prevention: Before vs After

| Scenario | Before Sprint 3 | After Sprint 3 |
|----------|-----------------|----------------|
| REPLAYABLE claim without recipe | Not detected | FAIL, blocks sprint |
| Missing execution_method | Not detected | FAIL, blocks sprint |
| Forbidden state jump (PRODUCT_SOURCE) | Not detected | FAIL, blocks sprint |
| MANUAL_UNGOVERNED with bad claim | Not detected | FAIL, blocks sprint |
| Governance-only sprint | False sample_output violation | PASS (exempt) |
| Legacy backfill | No guidance | PASS (accepted) |
