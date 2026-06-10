# Command Validator Hardening — Skills R106 (Lane F)

## Summary
19 new tests added for command validation and transcript validation hardening.

## Tests Added

### Command Section Coverage Tests (4)
1. `test_required_sections_count` — Verifies exactly 12 section types
2. `test_all_section_ids_present` — Verifies all expected section IDs
3. `test_error_severity_sections` — Verifies error-level sections block validation
4. `test_warning_severity_sections` — Verifies warning-level sections are logged

### Command File Negative Tests (4)
1. `test_missing_purpose_heading` — Catches missing title heading
2. `test_missing_forbidden_paths` — Catches missing forbidden paths section
3. `test_empty_file_fails` — Catches empty command files
4. `test_file_under_10_lines_fails` — Catches too-short files

### Registry Cross-Reference Tests (3)
1. `test_real_registry_has_no_missing_active_commands` — All active skills have command files
2. `test_orphan_commands_are_documented` — Orphan commands detected correctly
3. `test_draft_skills_allowed_missing_commands` — Draft/deferred skills don't produce errors

### Transcript Validator Hardening Tests (6)
1. `test_unregistered_skill_fails` — Unknown skill_id rejected
2. `test_invalid_result_value_fails` — Invalid result values rejected
3. `test_src_editing_tracks_are_correct` — SRC_EDITING_TRACKS includes all product tracks
4. `test_all_required_fields_documented` — REQUIRED_FIELDS matches contract
5. `test_directory_validation_empty_dir` — Empty directory returns 0
6. `test_directory_validation_with_non_json` — Non-JSON files ignored

### Full Validation Integration Tests (2)
1. `test_all_commands_pass_validation` — All command files pass
2. `test_passing_count_matches_total` — Zero failures

## Validator Changes
- `validate_claude_commands.py`: Added `"deferred"` to accepted non-error statuses in `cross_reference_registry()`

## Test File
`tests/python/supervisor/test_r106_command_validator_hardening.py` — 19 tests, all pass
