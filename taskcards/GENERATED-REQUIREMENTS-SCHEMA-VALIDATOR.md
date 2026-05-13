# Taskcard: Generated Requirements Schema and Validator
**ID:** GENERATED-REQUIREMENTS-SCHEMA-VALIDATOR
**Lane:** R2
**Status:** completed
**Completed:** 2026-05-13

## Objective
Build JSON schemas and a validator tool for AI-generated format requirements files.

## Deliverables
- [x] `schemas/generated-requirements/commercial-format-requirements.schema.json`
- [x] `schemas/generated-requirements/object-model-requirements.schema.json`
- [x] `schemas/generated-requirements/save-edit-requirements.schema.json`
- [x] `schemas/generated-requirements/conversion-requirements.schema.json`
- [x] `tools/requirements/validate_generated_requirements.py`
- [x] `tests/requirements/test_validate_generated_requirements.py`

## Key Validation Rules
- Required fields: requirement_id, format, capability_level, requirement_type, title, description, product_goal_mapping, source_evidence, source_type, confidence, status
- AI_PROPOSAL cannot be ACCEPTED without verifier approval
- ACCEPTED_FOR_VERTICAL_SLICE requires test_requirements
- Conversion requirements (sprint_scope: current) cannot be ACCEPTED_FOR_VERTICAL_SLICE
- Duplicate requirement IDs rejected

## Test Coverage
- 8 manual validation tests
- 7 integration tests against FODS and FODT generated YAML files
