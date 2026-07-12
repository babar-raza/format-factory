# Prompt-Skill Enforcement Report — FIOP-FULL-001
**Date:** 2026-07-12  
**Mission:** FIOP-FULL-001

## /found-issue-ownership Skill Status
- **Skill ID:** `found-issue-ownership`  
- **Command:** `/found-issue-ownership`  
- **Command file:** `.claude/commands/found-issue-ownership.md`  
- **Status:** active  
- **Product track:** machinery_governance  
- **Source:** `.supervisor/skill-registry.yaml` line 3291

**mandatory_validations:**
- found_issue_registered
- root_cause_identified
- healing_verified

## Validator Coverage
**Expected validator count:** 187 (`_EXPECTED_VALIDATOR_COUNT` in `governance_validator_runner.py`)  
**Active validators (empty declaration run):** 189 validators executed (169 PASS + 20 WARN + 0 FAIL)

Note: 189 > 187 because some validators execute multiple rule variants within one registered entry.

## Section-21 Validators (TC-FIOP-005) — Confirmed Active
| Rule ID | Function | Domain | Result on empty decl |
|---------|----------|--------|-----------------------|
| V_VALIDATE_FI_TASK_CLOSURE_UNACCOUNTED | validate_found_issue_task_closure_unaccounted | found_issue | PASS |
| V_VALIDATE_FI_NO_DELETED_TEST | validate_found_issue_no_deleted_test_without_analysis | found_issue | PASS |
| V_VALIDATE_FI_DOWNSTREAM_PATCH | validate_found_issue_downstream_patch_while_upstream_defective | found_issue | PASS |
| V_VALIDATE_FI_CLOSURE_NO_VERIFY | validate_found_issue_closure_without_verification | found_issue | PASS |
| V_VALIDATE_FI_UNTASKCARDED_REPORT | validate_found_issue_untaskcarded_in_final_report | found_issue | PASS |
| V_VALIDATE_FI_FIXTURE_EDIT | validate_found_issue_no_fixture_edit_without_authority | found_issue | PASS |

All 6 Section-21 validators confirmed registered (`@validator` decorator) and passing the count invariant test.

## Verification Commands
```
# Confirm validator count
cd tools/supervisor && .venv/Scripts/python -c "from governance_validator_runner import get_expected_validator_count; print(get_expected_validator_count())"
# => 187

# Confirm registry count >= 90% threshold
.venv/Scripts/pytest tests/supervisor/test_governance_validators.py -k count_invariant -v
# => PASSED
```
