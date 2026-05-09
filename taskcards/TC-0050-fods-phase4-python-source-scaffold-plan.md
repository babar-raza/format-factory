---
artifact_id: TC-0050-fods-phase4-python-source-scaffold-plan
artifact_type: taskcard
path: taskcards/TC-0050-fods-phase4-python-source-scaffold-plan.md
format_id: fods
product_family: cells
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
notes: "FODS Phase 4 Python source scaffold plan taskcard. Created run050. Completed run051."
---

# TC-0050: FODS Phase 4 -- Python Source Scaffold Plan

**Taskcard ID:** TC-0050
**Status:** completed (run051, 2026-05-09)
**Gate:** Post-Gate 10
**Format:** FODS

## Description
Create FODS Python FOSS product source at src/python/fods/.
Input: FUL package (6 files), tier-map.yaml, gate10-packaging-plan.md.

## Preconditions
- Gate 10 planning approved (YES, run048)
- Explicit Phase 4 Python implementation prompt (YES, run051)
- FUL package valid (YES, run050 -- 20/20 facts/reqs)

## Completed Source Path
    src/python/fods/
        __init__.py, parser.py, neutral_model.py, constants.py, exceptions.py, README.md

## Test Suite
    tests/python/conftest.py
    tests/python/fods/test_parser_basic.py
    tests/python/fods/test_parser_malformed.py
    tests/python/fods/test_parser_security.py
    tests/python/fods/test_neutral_model.py
    tests/python/fods/test_public_api.py

## Key Design Decisions
- iterparse streaming (not ET.parse) -- IR-FODS-002
- defusedxml optional import with fallback -- IR-FODS-004
- parse_fods() never raises; parse_fods_strict() raises FodsError subclasses
- No __init__.py in tests/python/fods/ (namespace collision fix)

## Requirements Coverage
- 19/20 IR-FODS requirements implemented
- IR-FODS-008 (formula evaluation) deferred to Tier 3 per tier-map.yaml

## Completion Artifacts
- src/python/fods/ (6 files: package + README); commit: d18e73e
- tests/python/fods/ (5 test files); commit: d18e73e
- tests/python/conftest.py; commit: d18e73e
- acquisition-packs/fods/phase4-traceability-matrix.md; commit: d18e73e
- tools/evidence/contracts/tc0050-fods-phase4-python-source.yaml; commit: d18e73e
