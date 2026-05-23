# TC-0058: Table Preservation — FODT Python Writer

**ID:** TC-0058-table-preservation-fodt
**Gap ID:** TC-TABLE-001
**Status:** CLOSED_VERIFIED
**Priority:** Medium
**Format:** FODT
**Track:** Python FOSS
**Sprint origin:** R49 (preservation matrix gap)
**Sprint target:** R51 or later

## Gap Description

Python FODT writer drops `<table:table>` blocks entirely on write. Documents containing
tables produce output with the table cells' plain text extracted (or omitted), but no
table structure (`<table:table-row>`, `<table:table-cell>`) is emitted.

## Evidence

- Preservation matrix: `reports/r49/preservation-matrix-fodt.md`
- Gap ID: TC-TABLE-001
- RISK-003 (active): Tables lost on Python FODT write

## Acceptance Criteria

1. A FODT file containing tables round-trips with table structure preserved.
2. `<table:table>`, `<table:table-row>`, `<table:table-cell>`, and `<table:table-column>`
   elements are emitted correctly.
3. Cell content (paragraphs and spans) within table cells is preserved.
4. At least 3 new tests covering table round-trip.

## Fix Scope

- `src/python/fodt/parser.py`: parse table blocks into structured dict
- `src/python/fodt/writer.py`: add table block emission branch

## Risk

RISK-003 partially resolved. Tables are now preserved on round-trip.

## Closure

**Closed:** R55, 2026-05-23 (advance from PARTIAL_PASS to PASS)
**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Evidence:**
- `_write_table()` in `src/python/fodt/writer.py` emits table:table/table-row/table-cell
- `content` unified sequence in neutral model fixes ordering (TC-0060)
- 8 table tests from R54 PASS; 2 new ordering tests confirm table position in doc
- `tests/python/fodt/test_r54_fodt_preservation.py`: 8/8 table tests PASS
- `tests/python/fodt/test_r55_fodt_spans_ordering.py`: ordering tests confirm table ordering
**Limitation:** cell styles not preserved (cosmetic — data content is preserved)
**Status:** CLOSED_VERIFIED
