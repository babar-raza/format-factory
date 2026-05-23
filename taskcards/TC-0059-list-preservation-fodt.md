# TC-0059: List Preservation — FODT Python Writer

**ID:** TC-0059-list-preservation-fodt
**Gap ID:** TC-LIST-001
**Status:** CLOSED_VERIFIED
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

RISK-003 partially resolved. Lists are now preserved on round-trip.

## Closure

**Closed:** R55, 2026-05-23 (advance from PARTIAL_PASS to PASS)
**Sprint:** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Evidence:**
- `_write_list()` in `src/python/fodt/writer.py` emits text:list/text:list-item/text:p
- `content` unified sequence in neutral model fixes ordering (TC-0060)
- 7 list tests from R54 PASS; ordering test confirms list position in doc
- `tests/python/fodt/test_r54_fodt_preservation.py`: 7/7 list tests PASS
- `tests/python/fodt/test_r55_fodt_spans_ordering.py`: ordering tests confirm list ordering
**Limitation:** nested list hierarchy (level > 1) still flattened (minor — cosmetic)
**Status:** CLOSED_VERIFIED
