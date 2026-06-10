# Handoff 004: add-python-object-model-feature / ppm / brightness_adjust

- **Handoff ID:** SKILLS-R103-HANDOFF-004
- **Skill:** add-python-object-model-feature
- **Format:** ppm
- **Feature:** brightness_adjust
- **Target Sprint:** R103
- **Description:** Add brightness_adjust(factor) scaling pixel values clamped to maxval

## Source Files
- src/python/ppm/ppm_parser.py

## Test Files
- tests/python/ppm/test_r103_ppm_brightness_adjust.py

## Acceptance Criteria
- 4+ tests, ledger entry
- Focused test passes
- Ledger entry added with SHA-256

## Forbidden Paths
- registry/format-registry.yaml
- plans/master-plan.md

## Rollback Plan
1. Revert source file changes
2. Remove test file
3. Remove ledger entry
