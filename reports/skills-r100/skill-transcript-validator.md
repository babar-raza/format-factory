# Train F: Skill Transcript Validator
Sprint: FORMAT-FACTORY-SKILLS-R100-GOVERNED-EXECUTION-DEEP-SKILL-SYSTEM-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Created

- `tools/supervisor/validate_skill_transcript.py` (130 lines)
- `tests/supervisor/test_validate_skill_transcript.py` (10 tests)

## Transcript Schema Enforced

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| invocation_id | string | YES | Unique ID for this invocation |
| skill_id | string | YES | Must match a registered skill |
| mode | string | YES | "dry-run" or "live" |
| inputs | dict | YES | Handoff field values |
| allowed_files | list | YES | Paths the skill was allowed to touch |
| actual_files_changed | list | YES | Paths actually changed |
| tests_run | list | YES | Test identifiers or commands |
| ledger_entry_id | string | conditional | Required for live src-editing skills |
| result | string | YES | "PASS" or "FAIL" |
| timestamp | string | optional | ISO 8601 timestamp |

## Validation Rules

1. All required fields present
2. mode in {dry-run, live}
3. result in {PASS, FAIL}
4. skill_id exists in registry
5. actual_files_changed subset of allowed_files
6. Live src-editing skills require ledger_entry_id
7. Inputs checked against required_handoff_fields (warning)

## Test Results

```
10 passed in 0.79s
```

| Test | Type | Result |
|------|------|--------|
| test_missing_required_fields | negative | PASS |
| test_invalid_mode | negative | PASS |
| test_invalid_result | negative | PASS |
| test_unregistered_skill | negative | PASS |
| test_files_outside_allowed | negative | PASS |
| test_live_src_editing_without_ledger | negative | PASS |
| test_valid_dry_run | positive | PASS |
| test_valid_live_with_ledger | positive | PASS |
| test_non_src_editing_skill_no_ledger_ok | positive | PASS |
| test_planning_skill_no_ledger_ok | positive | PASS |
