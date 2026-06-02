---
sprint: R91
generated_by: r91-worker
---

# Skill Registry Expansion

## Summary

`.supervisor/skill-registry.yaml` expanded with 11 new skill entries to cover all current product and automation work patterns.

## New Skills Added

### add-dotnet-object-model-feature

```yaml
skill: add-dotnet-object-model-feature
allowed_paths:
  - src/net/{format}/
  - tests/net/{format}/
forbidden_paths:
  - src/python/
  - registry/
required_inputs:
  - format_name
  - feature_name
  - api_signature
evidence_outputs:
  - tests/net/{format}/{Format}R{sprint}{Feature}Tests.cs
  - .local/evidences/{run_id}/dotnet-test-output.txt
required_tests: 3
ledger_requirements: true
rollback: revert src/net/{format}/ changes and delete test file
stop_conditions:
  - external_gate_required
  - test_count_below_minimum
```

### add-python-object-model-feature

```yaml
skill: add-python-object-model-feature
allowed_paths:
  - src/python/{format}/
  - tests/python/{format}/
forbidden_paths:
  - src/net/
  - registry/
required_inputs:
  - format_name
  - feature_name
  - function_signature
evidence_outputs:
  - tests/python/{format}/test_r{sprint}_{feature}.py
  - .local/evidences/{run_id}/python-test-output.txt
required_tests: 3
ledger_requirements: true
rollback: revert src/python/{format}/ changes and delete test file
stop_conditions:
  - external_gate_required
  - test_count_below_minimum
```

### add-same-format-writer-feature

```yaml
skill: add-same-format-writer-feature
allowed_paths:
  - src/net/{format}/
  - src/python/{format}/
  - tests/net/{format}/
  - tests/python/{format}/
forbidden_paths:
  - registry/
  - product-capability-matrix/
required_inputs:
  - format_name
  - track (net|python)
  - writer_method_name
evidence_outputs:
  - tests/{track}/{format}/test_r{sprint}_writer.py
required_tests: 3
ledger_requirements: true
rollback: revert writer implementation and delete tests
stop_conditions:
  - external_gate_required
```

### add-roundtrip-test

```yaml
skill: add-roundtrip-test
allowed_paths:
  - tests/net/{format}/
  - tests/python/{format}/
forbidden_paths:
  - src/
required_inputs:
  - format_name
  - track
  - roundtrip_scenario
evidence_outputs:
  - tests/{track}/{format}/test_r{sprint}_roundtrip.py
required_tests: 2
ledger_requirements: false
rollback: delete test file
stop_conditions: []
```

### add-installed-package-example

```yaml
skill: add-installed-package-example
allowed_paths:
  - examples/python/{format}/
  - examples/net/{format}/
forbidden_paths:
  - src/
  - tests/
required_inputs:
  - format_name
  - track
  - workflow_description
evidence_outputs:
  - examples/{track}/{format}/installed_workflow.py
required_tests: 1
ledger_requirements: false
rollback: delete example file
stop_conditions: []
```

### promote-gap-to-taskcard

```yaml
skill: promote-gap-to-taskcard
allowed_paths:
  - product-capability-matrix/
  - .supervisor/fixtures/
forbidden_paths:
  - src/
  - tests/
required_inputs:
  - gap_id
  - format_name
  - proposed_sprint
evidence_outputs:
  - product-capability-matrix/taskcard-{gap_id}.yaml
required_tests: 0
ledger_requirements: false
rollback: delete taskcard file
stop_conditions: []
```

### generate-execution-handoff

```yaml
skill: generate-execution-handoff
allowed_paths:
  - reports/supervisor/
  - .local/supervisor/
forbidden_paths:
  - src/
  - tests/
required_inputs:
  - handoff_reason
  - blocking_item
evidence_outputs:
  - reports/supervisor/handoff-{timestamp}.md
required_tests: 0
ledger_requirements: false
rollback: delete handoff file
stop_conditions: []
```

### grade-work-item

```yaml
skill: grade-work-item
allowed_paths:
  - reports/supervisor/
  - .local/supervisor/
forbidden_paths:
  - src/
required_inputs:
  - work_item_id
  - declaration_path
evidence_outputs:
  - reports/supervisor/work-item-grades.json
  - reports/supervisor/work-item-grades.md
required_tests: 0
ledger_requirements: false
rollback: delete grade output files
stop_conditions: []
```

### select-poc-gap

```yaml
skill: select-poc-gap
allowed_paths:
  - .local/supervisor/
  - reports/supervisor/
forbidden_paths:
  - src/
required_inputs:
  - format_filter (optional)
evidence_outputs:
  - .local/supervisor/selected-product-gaps.json
  - reports/supervisor/product-gap-selection.md
required_tests: 0
ledger_requirements: false
rollback: restore prior selected-product-gaps.json
stop_conditions: []
```

### verify-dogfood-path

```yaml
skill: verify-dogfood-path
allowed_paths:
  - tests/net/{format}/
  - tests/python/{format}/
forbidden_paths:
  - src/
required_inputs:
  - format_name
  - track
  - library_path
evidence_outputs:
  - tests/{track}/{format}/test_r{sprint}_dogfood_path.py
required_tests: 1
ledger_requirements: false
rollback: delete test file
stop_conditions: []
```

### package-install-proof

```yaml
skill: package-install-proof
allowed_paths:
  - examples/python/{format}/
  - .local/evidences/{run_id}/
forbidden_paths:
  - src/
required_inputs:
  - format_name
  - package_name
evidence_outputs:
  - .local/evidences/{run_id}/install-proof-{format}.txt
required_tests: 1
ledger_requirements: false
rollback: delete proof file
stop_conditions: []
```
