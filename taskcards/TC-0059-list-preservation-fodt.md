# TC-0059: List Preservation — FODT Python Writer

**ID:** TC-0059-list-preservation-fodt
**Gap ID:** TC-LIST-001
**Status:** OPEN
**Priority:** Medium
**Format:** FODT
**Track:** Python FOSS
**Sprint origin:** R49 (preservation matrix gap)
**Sprint target:** R51 or later

## Gap Description

Python FODT writer loses `<text:list>` structure on write. Ordered and unordered list
items are emitted as plain paragraphs without list markers, or omitted entirely.
The list hierarchy (`<text:list-item>`, `<text:list-header>`) is not preserved.

## Evidence

- Preservation matrix: `reports/r49/preservation-matrix-fodt.md`
- Gap ID: TC-LIST-001
- RISK-003 (active): Lists lost on Python FODT write

## Acceptance Criteria

1. A FODT file containing ordered and unordered lists round-trips with list structure preserved.
2. `<text:list>`, `<text:list-item>` hierarchy is emitted correctly.
3. List style names (`text:style-name`) are preserved.
4. At least 3 new tests covering list round-trip.

## Fix Scope

- `src/python/fodt/parser.py`: parse list blocks into structured dict
- `src/python/fodt/writer.py`: add list block emission branch

## Risk

RISK-003 (active). Until fixed, documents with lists should use the .NET commercial track.
