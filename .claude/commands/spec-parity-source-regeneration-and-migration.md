# /spec-parity-source-regeneration-and-migration

**Skill ID:** spec-parity-source-regeneration-and-migration
**Registry Version:** 2.0
**Track:** spec_parity
**Status:** active

## Purpose

Regenerate or migrate existing source code to match the spec-shaped blueprint.
Enforces that all model classes have a `canonical_namespace` and `spec_qname`.
Arbitrary flat classes for spec concepts are FORBIDDEN.

## Required Inputs

- `format_id` — format being migrated
- `blueprint_path` — path to the spec-shaped blueprint YAML
- `exact_source_paths` — files to modify (must be pre-approved)
- `exact_test_paths` — test files proving the migration
- `ledger_entry_path` — product code ledger entry to create

## Mandatory Validations

1. `product_code_ledger_validator` — ledger entry must pass validator
2. `spec_parity_validator_pass` — no flat class violations
3. `no_flat_class_violations` — zero flat class violations after migration
4. `focused_tests_pass` — all tests in exact_test_paths must pass

## Rules

- Do NOT migrate more than the declared scope in one invocation
- Do NOT change API signatures that would break existing tests
- Reduced-scope migrations must use `/python-reduced-spec-parity-model` instead
- Commercial (.NET) migrations require Gate 11 preparation (not approval)

## Evidence Requirements

- Source diff/patch of changes
- Spec parity validator run output
- Test log showing all tests pass
- Ledger entry JSON

## Allowed Paths

- `src/python/<format>/` (declared exact_source_paths only)
- `tests/python/<format>/` (declared exact_test_paths only)
- `reports/r90/product-code-change-ledger.json`
- `.local/evidences/<run_id>/`

## Forbidden Paths

- No edits outside `exact_source_paths` and `exact_test_paths`
- No API signature changes that would break existing tests
- No Gate 11 commercial paths without Gate 11 preparation packet

## Stop Conditions

- Stop if `blueprint_path` does not exist
- Stop if any test in `exact_test_paths` fails after migration
- Stop if `product_code_ledger_validator` exits non-zero
- Stop if flat class violations remain after migration (must be zero)

## Gate 11

This skill prepares spec-parity evidence for Gate 11 readiness packets.
Actual Gate 11 EXECUTION approval requires Babar Raza.
