# T-SCHEMA-01 Evidence

## What was done
Added `_validate_jsonschema()` function to `tools/supervisor/evidence_declaration.py`. Called at the top of `validate_schema()`. Graceful degradation if jsonschema library not installed.

## Evidence
- Function attempts `jsonschema.validate(decl, schema)` against `.supervisor/schemas/evidence-declaration.schema.json`
- ImportError caught silently (library optional)
- Any validation error returned in errors list
- Tests: 84/84 passing (no regression from schema enforcement addition)
