# Generated Requirements Schema and Validator — Report
**Lane R2**
**Date:** 2026-05-13

## Summary

Built JSON Schema definitions and a Python validator for AI-generated format requirements files.

## Schemas

| Schema | Path | Purpose |
|--------|------|---------|
| Commercial requirements | `schemas/generated-requirements/commercial-format-requirements.schema.json` | Main requirements validation |
| Object model | `schemas/generated-requirements/object-model-requirements.schema.json` | Entity definitions |
| Save/edit | `schemas/generated-requirements/save-edit-requirements.schema.json` | Save/edit requirements |
| Conversion | `schemas/generated-requirements/conversion-requirements.schema.json` | Future-scoped conversion |

## Validator

`tools/requirements/validate_generated_requirements.py`

### Key Validation Rules
1. Required fields present on every requirement
2. Unique requirement IDs within each file
3. product_goal_mapping non-empty
4. source_evidence required (except PRODUCT_DECISION)
5. AI_PROPOSAL cannot be ACCEPTED without verifier approval
6. ACCEPTED_FOR_VERTICAL_SLICE requires test_requirements
7. Conversion requirements with sprint_scope: current cannot be ACCEPTED_FOR_VERTICAL_SLICE

## Tests

`tests/requirements/test_validate_generated_requirements.py`

- 8 unit tests for manual validation rules
- 7 integration tests against actual FODS and FODT YAML files

## Artifacts

- `schemas/generated-requirements/` (4 schemas)
- `tools/requirements/validate_generated_requirements.py`
- `tests/requirements/test_validate_generated_requirements.py`
