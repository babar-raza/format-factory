# Validator Hardening Campaign (Skills R104 Wave 3)

## Results Summary

| Validator | Result | Details |
|-----------|--------|---------|
| Command file validator | 23/23 PASS | All commands (incl. 5 new) fully complete (12/12 sections) |
| Transcript validator (R103 transcripts) | 13/15 PASS, 2 FAIL | 2 anti-bypass demos FAIL as expected |
| All supervisor tests | 50/50 PASS | 29 existing + 21 new R104 tests |

## New Tests Added (21)

### TestPromotedSkillCommandFiles (15 parametrized)
- 5x `test_promoted_command_file_passes` — each promoted command validates
- 5x `test_promoted_command_has_all_12_sections` — complete section coverage
- 5x `test_promoted_command_has_frontmatter` — version + last-updated present

### TestPromotedSkillRegistryConsistency (3)
- `test_registry_has_promoted_skills_as_active` — 5 promoted skills are active
- `test_deferred_skills_remain_draft` — 2 deferred skills stay draft
- `test_total_active_skills_is_18` — total active count correct

### TestCommandValidatorNegative (3)
- `test_missing_allowed_paths_in_stub_fails` — incomplete command file detected
- `test_too_short_file_fails` — trivially short files rejected
- `test_nonexistent_file_fails` — missing files handled gracefully

## Validator Results Files

- `validator-results/command-validation-r104.json` — full command validation output
- `validator-results/transcript-validation-r103-transcripts.json` — R103 transcript re-validation
- `raw-logs/test-validators-all.log` — complete pytest output

## Warnings (not blocking)

- 5 orphan commands (legacy, not in registry): evidence-review-next-prompt, execution-handoff, export-plan-context, memory-sprint, plan-hardening
- 2 draft skills have no command files (acceptable for draft): record-lane-execution, check-mcp-status
- update-capability-matrix contains gate status claims (cosmetic)
