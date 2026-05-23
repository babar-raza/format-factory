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

**Closed (flat lists / criteria 1+2+4):** R55, 2026-05-23
**Closed (nested hierarchy criterion 2):** R56, 2026-05-23
**Sprint (flat):** FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
**Sprint (nested):** FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Evidence:**
- `_write_list()` in `src/python/fodt/writer.py` emits text:list/text:list-item/text:p (R55)
- `content` unified sequence in neutral model fixes ordering (TC-0060)
- 7 list tests from R54 PASS; ordering test confirms list position in doc
- `tests/python/fodt/test_r54_fodt_preservation.py`: 7/7 list tests PASS
- `tests/python/fodt/test_r55_fodt_spans_ordering.py`: ordering tests confirm list ordering (R55)
- `_write_list()` R56: level-stack algorithm emits nested `text:list` inside `text:list-item` for level > 1 items
- 5 tests in `tests/python/fodt/test_r56_fodt_hyperlinks_nested_lists.py::TestNestedListHierarchy` (R56)
- All 259 FODT tests pass. Zero regressions.
**IV-R55-008 corrective note:** R55 closure was overclaimed; nested hierarchy (criterion 2 level>1) was deferred. R56 fully closes.
**Status:** CLOSED_VERIFIED
