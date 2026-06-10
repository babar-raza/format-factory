# Train A: Skill Registry Audit Report
Sprint: FORMAT-FACTORY-SKILLS-R99-SKILL-REGISTRY-GOVERNED-EXECUTION-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Registry Overview

- Registry ID: r98-governed-skills-expanded
- Registry Status: active_fail_closed
- Total Skills: 13
- Registry Version: 2.0
- Last Updated: 2026-06-02

## Skill-by-Skill Audit

### 1. add-dotnet-api
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/add-dotnet-api.md) |
| purpose | PRESENT (bounded .NET API addition) |
| inputs | format_id, api_name, exact_source_paths, exact_test_paths, ledger_entry_path, focused_test_command |
| allowed_paths | PRESENT (src/net/<format_id>/, tests/net/<format_id>/) |
| forbidden_paths | PRESENT (src/python/**, gate files, registry) |
| output_files | ledger record, test results |
| required_tests | YES (3-case: normal, boundary, invalid-input) |
| ledger_requirements | YES (pre-execution check + post-execution record) |
| POC_matrix_requirements | YES (matrix update if status changes) |
| rollback | MISSING |
| refusal_rules | YES (stop on gate/release changes) |
| sample_invocation | MISSING |
| **Classification** | **READY** |

### 2. add-python-api
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/add-python-api.md) |
| purpose | PRESENT (bounded Python API addition) |
| inputs | format_id, api_name, exact_source_paths, exact_test_paths, ledger_entry_path, focused_test_command |
| allowed_paths | PRESENT (src/python/<format_id>/, tests/python/<format_id>/) |
| forbidden_paths | PRESENT (src/net/**, gate files) |
| output_files | ledger record, test results |
| required_tests | YES (3-case coverage) |
| ledger_requirements | YES |
| POC_matrix_requirements | YES |
| rollback | MISSING |
| refusal_rules | YES |
| sample_invocation | MISSING |
| **Classification** | **READY** |

### 3. add-dogfood-export
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/add-dogfood-export.md) |
| purpose | PRESENT (FF-library-backed export) |
| inputs | source_format_id, target_format_id, export_name, target_ff_library, exact_source_paths, exact_test_paths, ledger_entry_path, focused_test_command |
| allowed_paths | PRESENT (src/python/<format>/) |
| forbidden_paths | PRESENT (raw serialization, PIL, OpenCV, openpyxl) |
| output_files | ledger record, dogfood status |
| required_tests | YES (reload, dependency absence, target writer, value survival) |
| ledger_requirements | YES |
| POC_matrix_requirements | YES |
| rollback | MISSING |
| refusal_rules | YES (backend must be FF library) |
| sample_invocation | MISSING |
| **Classification** | **READY** |

### 4. update-capability-matrix
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/update-capability-matrix.md) |
| purpose | PRESENT (reconcile POC results into matrix) |
| inputs | matrix_entry, evidence_paths, focused_validation_commands, claimed_status_changes |
| allowed_paths | PRESENT (product-capability-matrix/) |
| forbidden_paths | PRESENT (gate authority, release authority, commercial readiness) |
| output_files | matrix YAML diff |
| required_tests | YES (focused validation rerun) |
| ledger_requirements | NO (matrix is reference, not src) |
| POC_matrix_requirements | YES (is the matrix) |
| rollback | MISSING |
| refusal_rules | YES |
| sample_invocation | MISSING |
| **Classification** | **READY** |

### 5. add-dotnet-object-model-feature
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/add-dotnet-object-model-feature.md) |
| purpose | PRESENT (object model feature) |
| inputs | format_id, feature_name, exact_source_paths, exact_test_paths, ledger_entry_path |
| allowed_paths | PRESENT (src/net/<format_id>/Model/**, Document.cs, tests) |
| forbidden_paths | PRESENT (src/python/**, gate files, registry, master-plan) |
| output_files | ledger record, test results |
| required_tests | YES (normal, boundary, invalid-input) |
| ledger_requirements | YES |
| POC_matrix_requirements | IMPLICIT |
| rollback | MISSING |
| refusal_rules | YES |
| sample_invocation | MISSING |
| **Classification** | **READY** |

### 6. add-python-object-model-feature
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/add-python-object-model-feature.md) |
| purpose | PRESENT (Python object model feature) |
| inputs | format_id, feature_name, exact_source_paths, exact_test_paths, ledger_entry_path |
| allowed_paths | IMPLIED (src/python/<format>/) |
| forbidden_paths | IMPLIED |
| output_files | ledger record, test results |
| required_tests | YES (at least 4 test functions) |
| ledger_requirements | YES (explicit JSON format shown) |
| POC_matrix_requirements | IMPLICIT |
| rollback | MISSING |
| refusal_rules | IMPLIED |
| sample_invocation | PRESENT |
| **Classification** | **READY** (frontmatter missing but functional) |

### 7. add-same-format-writer-feature
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/add-same-format-writer-feature.md) |
| purpose | PRESENT (same-format save/write) |
| inputs | format_id, writer_scope, exact_source_paths, exact_test_paths, ledger_entry_path |
| allowed_paths | IMPLIED |
| forbidden_paths | IMPLIED |
| output_files | ledger record, roundtrip test |
| required_tests | YES (at least 4 tests, roundtrip) |
| ledger_requirements | YES |
| POC_matrix_requirements | IMPLICIT |
| rollback | MISSING |
| refusal_rules | IMPLIED |
| sample_invocation | PRESENT |
| **Classification** | **READY** (frontmatter missing but functional) |

### 8. add-roundtrip-test
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/add-roundtrip-test.md) |
| purpose | PRESENT (parse-edit-write-reparse test) |
| inputs | format_id, roundtrip_scope, exact_test_paths |
| allowed_paths | PRESENT (tests only) |
| forbidden_paths | PRESENT (src/**, gate files) |
| output_files | test file |
| required_tests | YES (load-edit-save-reload-assert) |
| ledger_requirements | NO (test-only; no src edits) |
| POC_matrix_requirements | NO |
| rollback | MISSING |
| refusal_rules | YES |
| sample_invocation | MISSING |
| **Classification** | **READY** |

### 9. add-installed-package-example
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/add-installed-package-example.md) |
| purpose | PRESENT (installed package example) |
| inputs | format_id, example_scope, example_path |
| allowed_paths | PRESENT (examples/python/<format>/, examples/net/<format>/) |
| forbidden_paths | PRESENT (src/**, gate files) |
| output_files | example file |
| required_tests | YES (smoke test, exit 0) |
| ledger_requirements | NO (examples, not src) |
| POC_matrix_requirements | NO |
| rollback | MISSING |
| refusal_rules | YES |
| sample_invocation | MISSING |
| **Classification** | **READY** |

### 10. promote-gap-to-taskcard
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/promote-gap-to-taskcard.md) |
| purpose | PRESENT (gap to taskcard promotion) |
| inputs | gap_id, taskcard_path |
| allowed_paths | IMPLIED (taskcards/) |
| forbidden_paths | IMPLIED |
| output_files | taskcard file |
| required_tests | YES (YAML well-formedness) |
| ledger_requirements | NO |
| POC_matrix_requirements | NO |
| rollback | MISSING |
| refusal_rules | IMPLIED |
| sample_invocation | PRESENT |
| **Classification** | **READY** (minimal but functional) |

### 11. generate-execution-handoff
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/generate-execution-handoff.md) |
| purpose | PRESENT (structured execution handoff) |
| inputs | skill_id, target_format, scope |
| allowed_paths | PRESENT (reports/) |
| forbidden_paths | IMPLIED |
| output_files | handoff document |
| required_tests | YES (YAML validity) |
| ledger_requirements | YES (PENDING_EXECUTION_HANDOFF entry) |
| POC_matrix_requirements | NO |
| rollback | MISSING |
| refusal_rules | IMPLIED |
| sample_invocation | PRESENT |
| **Classification** | **READY** (frontmatter missing) |

### 12. verify-dogfood-path
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/verify-dogfood-path.md) |
| purpose | PRESENT (FF-library-only verification) |
| inputs | export_name, source_format, target_format, exact_test_paths |
| allowed_paths | IMPLIED (tests/python/<format>/) |
| forbidden_paths | IMPLIED |
| output_files | test results, dogfood matrix status |
| required_tests | YES (import + export) |
| ledger_requirements | CONDITIONAL (if src changes needed) |
| POC_matrix_requirements | YES |
| rollback | MISSING |
| refusal_rules | YES (no external imaging backends) |
| sample_invocation | PRESENT |
| **Classification** | **READY** (was UNSAFE, now fixed - added product_code_ledger_validator) |

### 13. package-install-proof
| Field | Status |
|-------|--------|
| skill_id | PRESENT |
| command_file | PRESENT (.claude/commands/package-install-proof.md) |
| purpose | PRESENT (wheel install + import proof) |
| inputs | format_id, package_name |
| allowed_paths | IMPLIED (packaging/) |
| forbidden_paths | IMPLIED |
| output_files | install output, import test result |
| required_tests | YES (import + API smoke) |
| ledger_requirements | NO |
| POC_matrix_requirements | NO |
| rollback | MISSING |
| refusal_rules | IMPLIED |
| sample_invocation | PRESENT |
| **Classification** | **READY** (minimal but appropriate) |

## Summary Table

| Skill ID | Classification | Frontmatter | Rollback | Sample | Ledger |
|----------|---------------|-------------|----------|--------|--------|
| add-dotnet-api | READY | YES | NO | NO | YES |
| add-python-api | READY | YES | NO | NO | YES |
| add-dogfood-export | READY | YES | NO | NO | YES |
| update-capability-matrix | READY | YES | NO | NO | N/A |
| add-dotnet-object-model-feature | READY | YES | NO | NO | YES |
| add-python-object-model-feature | READY | NO | NO | YES | YES |
| add-same-format-writer-feature | READY | NO | NO | YES | YES |
| add-roundtrip-test | READY | YES | NO | NO | N/A |
| add-installed-package-example | READY | YES | NO | NO | N/A |
| promote-gap-to-taskcard | READY | NO | NO | YES | N/A |
| generate-execution-handoff | READY | NO | NO | YES | YES |
| verify-dogfood-path | READY | NO | NO | YES | CONDITIONAL |
| package-install-proof | READY | NO | NO | YES | N/A |

## Key Findings

1. **All 13 skills READY** after the verify-dogfood-path ledger fix
2. **Missing rollback** in all 13 skills (systematic gap)
3. **Missing frontmatter** in 6 of 13 skills (add-python-object-model-feature, add-same-format-writer-feature, verify-dogfood-path, package-install-proof, generate-execution-handoff, promote-gap-to-taskcard)
4. **Missing sample invocation** in 8 of 13 skills
5. **Ledger enforcement defect**: verify-dogfood-path was UNSAFE (cross_product_export track without ledger validation) -- FIXED in this sprint
6. **Validator defect**: R98-GOVERNED-DOTNET-NETPBM-SAVETOFILE-001 uses state "modified" instead of "present" -- FOUND by ledger validator

## Repairs Made in This Sprint

1. verify-dogfood-path: Added `product_code_ledger_validator` to mandatory_validations
2. Skill registry validator created: `tools/supervisor/validate_skill_registry.py`
3. Skill registry schema created: `.supervisor/schemas/skill-registry.schema.json`

## Validator Results

```
SKILL_REGISTRY_VALIDATION: PASS
  total=13 ready=13 partial=0 placeholder=0 missing=0 unsafe=0
```
