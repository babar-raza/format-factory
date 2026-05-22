# TC-0058: Table Preservation — FODT Python Writer

**ID:** TC-0058-table-preservation-fodt
**Gap ID:** TC-TABLE-001
**Status:** OPEN
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

RISK-003 (active). Until fixed, documents with tables should use the .NET commercial track.
