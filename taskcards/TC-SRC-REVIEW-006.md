# TC-SRC-REVIEW-006: Tests — Existing API and New QName Model

**Lane**: SRC-REVIEW
**Status**: backlog
**Owner**: autonomous agent
**Prerequisites**: TC-SRC-REVIEW-005 COMPLETE
**item_type**: GOVERNANCE_ASSET
**gap_ledger_ref**: GAP-QNAME-FODT-004

## Objective

Create all required tests to verify existing FODT API is unchanged AND the new QName spec stubs exist
with correct attributes.

## Tests to Create

### tests/spec_registry/test_schema_validation.py
- schema.yaml is valid YAML
- schema.yaml file exists at shared/qname-registry/schema.yaml

### tests/spec_registry/test_fodt_registry.py
- 9 QNames present in fodt.yaml (or 6 if table entries deferred)
- All spec_fact_refs resolvable in fodt-context-pack.json

### tests/python/fodt/test_spec_qname_stubs.py
- All 8 Python stub files exist with correct spec_qname values
- All 4 __init__.py files exist in spec/ subdirectories
- `from fodt.spec.text.paragraph import Paragraph; assert Paragraph.spec_qname == "text:p"`

### tests/python/fodt/test_compat_bootstrap.py (KEY SAFETY TEST)
- `from fodt.compat import FodtParagraph` succeeds
- Imported FodtParagraph has .kind, .text, .spans properties
- Proves compat.py is NOT accidentally importing architecture_only stubs

### tests/python/fodt/test_fodt_backward_compat.py
- All existing parse_fodt tests pass (models.py unchanged)

### tests/spec/test_generate_canonical_stubs.py
- Idempotency: run generate_canonical_stubs.py twice → identical file contents
- __init__.py exists in all spec/ subdirectories
- No overwrite of implementing or implemented status files

## Validation

All test files pass with `.venv/Scripts/pytest <path>`

## Evidence Required

- Pytest output for each test file showing PASS

## Completion Criteria

All tests pass; existing parse_fodt tests unaffected
