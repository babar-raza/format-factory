# Skill System Truth Map (R102 Wave 0)

## Skill Registry State

| Category | Count | Status |
|----------|-------|--------|
| Total skills | 20 | In registry |
| Active skills | 13 | Command file exists, 12/12 sections |
| Draft skills | 7 | Missing command files (acceptable) |
| Orphan commands | 5 | In `.claude/commands/` but not in registry |
| Command validation PASS | 13/18 | 5 legacy files unhardened |

## Command File Compliance

### Fully Compliant (12/12 sections)
1. add-dogfood-export.md (v1.2)
2. add-dotnet-api.md (v1.2)
3. add-dotnet-object-model-feature.md (v1.2)
4. add-installed-package-example.md (v1.1)
5. add-python-api.md (v1.2)
6. add-python-object-model-feature.md (v1.2)
7. add-roundtrip-test.md (v1.0)
8. add-same-format-writer-feature.md (v1.1)
9. generate-execution-handoff.md (v1.1)
10. package-install-proof.md (v1.1)
11. promote-gap-to-taskcard.md (v1.1)
12. update-capability-matrix.md (v1.2)
13. verify-dogfood-path.md (v1.1)

### Non-Compliant (legacy, not governed)
14. evidence-review-next-prompt.md — missing: inputs, allowed_paths, forbidden_paths, stop_conditions, rollback, transcript, sample
15. execution-handoff.md — missing: inputs, allowed_paths, forbidden_paths, stop_conditions, rollback, transcript, sample
16. export-plan-context.md — missing: inputs, allowed_paths, forbidden_paths, stop_conditions, rollback, transcript
17. memory-sprint.md — missing: inputs, allowed_paths, forbidden_paths, stop_conditions, rollback, transcript, sample
18. plan-hardening.md — missing: inputs, allowed_paths, forbidden_paths, stop_conditions, rollback, transcript, sample

## Validator Inventory

| Validator | File | Tests | Status |
|-----------|------|-------|--------|
| Command file validator | tools/supervisor/validate_claude_commands.py | 12 | PASS |
| Transcript validator | tools/supervisor/validate_skill_transcript.py | 0 (no test file) | NEEDS TESTS |
| Registry validator | (inline in validate_claude_commands.py) | via command validator | PASS |
| Ledger validator | tools/supervisor/validate_product_code_ledger.py | existing | PASS (skills stream) |
| Context-pack validator | tools/supervisor/build_context_pack.py | N/A | NOT YET SKILL-AWARE |

## Transcript Schema Gap

R101 transcripts use **wrong schema**:
- `transcript_id` instead of `invocation_id`
- `verdict` instead of `result`
- Missing: `allowed_files`, `actual_files_changed`, `forbidden_files`, `rollback_plan`
- Nested `execution.tests_run` instead of flat `tests_run`

R102 transcripts use **correct schema** matching `validate_skill_transcript.py`:
- `invocation_id`, `skill_id`, `mode`, `inputs`, `allowed_files`, `actual_files_changed`, `tests_run`, `result`

## Anti-Bypass Coverage

| Demo | Mode | Expected Result | Validator Confirms |
|------|------|-----------------|-------------------|
| BACKFILLED_PRE_GOVERNANCE | anti-bypass-demo | FAIL | Yes (skill_id not in registry) |
| add-magic-feature | anti-bypass-demo | FAIL | Yes (skill_id not in registry) |
| NOTE: validator rejects `anti-bypass-demo` mode | | | Needs mode expansion |

## Package Self-Containment

R101 review package contained: manifests and declaration YAML only.
R101 review package DID NOT contain: transcripts, handoffs, command files, validator results, raw logs.

R102 target: all artifacts physically in ZIP.
