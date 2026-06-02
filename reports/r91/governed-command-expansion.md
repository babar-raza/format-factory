---
sprint: R91
generated_by: r91-worker
---

# Governed Command Expansion

## Summary

Six new governed commands created under `.claude/commands/`. Each command encodes the full governance contract for its skill so agents can invoke them without re-reading the skill registry.

## Commands Created

### .claude/commands/add-dotnet-object-model-feature.md

Input schema:
- `format_name`: string — format folder name under src/net/
- `feature_name`: string — PascalCase feature name
- `api_signature`: string — full C# method signature

Allowed files:
- `src/net/{format_name}/{FormatName}Document.cs` or equivalent model file
- `tests/net/{format_name}/{FormatName}R{sprint}{FeatureName}Tests.cs`

Forbidden files: any file outside `src/net/{format_name}/` or `tests/net/{format_name}/`

Required evidence:
- Test file with at least 3 passing tests
- dotnet test output captured to `.local/evidences/{run_id}/dotnet-test-output.txt`

Required tests: minimum 3, all must pass

Product-code ledger requirement: ledger entry with item_id matching `R{sprint}-GOVERNED-{FORMAT}-NET-{FEATURE}-001` must be written before the source edit

Rollback guidance: revert `src/net/{format_name}/` changes and delete the test file; do not leave partial implementations

Refusal condition: refuse if feature requires external API, credential, or Gate 8/11 approval

---

### .claude/commands/add-python-object-model-feature.md

Input schema:
- `format_name`: string — format folder name under src/python/
- `feature_name`: string — snake_case feature name
- `function_signature`: string — full Python def signature

Allowed files:
- `src/python/{format_name}/{feature_name}.py` or existing model file
- `tests/python/{format_name}/test_r{sprint}_{feature_name}.py`

Forbidden files: any file outside `src/python/{format_name}/` or `tests/python/{format_name}/`

Required evidence:
- Test file with at least 3 passing tests
- pytest output captured to `.local/evidences/{run_id}/python-test-output.txt`

Required tests: minimum 3, all must pass

Product-code ledger requirement: ledger entry with item_id matching `R{sprint}-GOVERNED-{FORMAT}-PY-{FEATURE}-001`

Rollback guidance: revert source changes and delete test file

Refusal condition: refuse if function requires network access or unpublished dependency

---

### .claude/commands/add-same-format-writer-feature.md

Input schema:
- `format_name`: string
- `track`: `net` or `python`
- `writer_method_name`: string — name of write/save method

Allowed files: source and test files for the specified format and track only

Forbidden files: files outside the format's source and test directories

Required evidence: test file proving write → re-read roundtrip produces equivalent content

Required tests: minimum 3 (write test, re-read test, roundtrip equivalence test)

Product-code ledger requirement: YES

Rollback guidance: revert writer method, delete roundtrip tests

Refusal condition: refuse if output format differs from input format (use add-dogfood-export instead)

---

### .claude/commands/add-roundtrip-test.md

Input schema:
- `format_name`: string
- `track`: `net` or `python`
- `roundtrip_scenario`: string — human description of what is round-tripped

Allowed files: test files only — no src/ changes

Forbidden files: any file under src/

Required evidence: test output showing parse→write→re-parse produces equivalent model

Required tests: minimum 2

Product-code ledger requirement: NO (test-only change)

Rollback guidance: delete the test file

Refusal condition: refuse if test requires a src change that is not already implemented

---

### .claude/commands/add-installed-package-example.md

Input schema:
- `format_name`: string
- `track`: `net` or `python`
- `workflow_description`: string — one-line description of what the example demonstrates

Allowed files: `examples/{track}/{format_name}/` only

Forbidden files: src/, tests/, registry/

Required evidence: example file that executes without error (import test or smoke test)

Required tests: 1 smoke test verifying imports work from installed package path

Product-code ledger requirement: NO

Rollback guidance: delete the example file

Refusal condition: refuse if example uses APIs not yet implemented in src/

---

### .claude/commands/promote-gap-to-taskcard.md

Input schema:
- `gap_id`: string — ID from poc-targets.yaml or gap selector output
- `format_name`: string
- `proposed_sprint`: string — suggested sprint label (e.g. R92)

Allowed files:
- `product-capability-matrix/taskcard-{gap_id}.yaml`
- `.supervisor/fixtures/r{sprint}-poc-gap-extraction.yaml` (append only)

Forbidden files: src/, tests/, registry/format-registry.yaml

Required evidence: taskcard YAML with gap_id, format_name, proposed_sprint, acceptance_criteria, skill_to_use

Required tests: 0

Product-code ledger requirement: NO

Rollback guidance: delete taskcard YAML and revert fixture append

Refusal condition: refuse if gap_id does not exist in current poc-targets.yaml
