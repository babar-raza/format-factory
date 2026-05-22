# Phase Audit 4 Continuation

**Sprint:** FORMAT-FACTORY-R53-SELF-VERIFYING-BASELINE-001
**Date:** 2026-05-22
**Phase:** 4 — FODS/FODT Implementation Quality (R51 audit)

## Previous Status (R52)

Phase 4 result: **CONDITIONAL_PASS**
Open TCs:
- TC-0054: FODS formula preservation — deferred to R53
- TC-0057: FODT heading preservation — deferred to R53
- TC-0058: FODT list preservation — deferred to R53
- TC-0059: FODT table preservation — deferred to R53

## R53 Progress

### TC-0054: FODS Formula Preservation — CLOSED

**Status: PASS**

- Parser already captured `formula` attribute (IR-FODS-008, line 314)
- Writer now emits `table:formula` attribute on round-trip (5-line fix in `_write_cell()`)
- 7 tests: `tests/python/fods/test_r53_formula_preservation.py` — all PASS
- Tests cover: capture, emit, full round-trip, edit-non-formula preserves formula, multiple formulas, verbatim preservation, non-formula has None

### TC-0057: FODT Heading Preservation — OPEN

**Status: NOT_MET**

FODT parser captures `text:outline-level` attribute. FODT writer (`src/python/fodt/writer.py`) does not emit heading attributes. Round-trip: headings become plain paragraphs.

**R54 plan:** Add `text:outline-level` emission in FODT writer for heading blocks.

### TC-0058: FODT List Preservation — OPEN

**Status: NOT_MET**

`list_traversal.py` collects list items. FODT writer does not emit `text:list` structure.

**R54 plan:** Implement list write-back in FODT writer.

### TC-0059: FODT Table Preservation — OPEN

**Status: NOT_MET**

FODT parser captures table rows/cells. FODT writer does not emit `table:table` elements.

**R54 plan:** Implement table write-back in FODT writer.

## Updated Phase 4 Status

| Format | Dimension | Status |
|--------|-----------|--------|
| FODS | Parser completeness | PASS (R50 audit) |
| FODS | Neutral model | PASS (R50 audit) |
| FODS | Writer/save | PASS (R50 audit) |
| FODS | Formula preservation (TC-0054) | **PASS (R53 closes)** |
| FODS | Fuzz/security (Gate 7) | PASS |
| FODT | Parser completeness | PASS (R50 audit) |
| FODT | Neutral model | PASS (R50 audit) |
| FODT | Writer/save | PASS (basic content) |
| FODT | Heading preservation (TC-0057) | OPEN |
| FODT | List preservation (TC-0058) | OPEN |
| FODT | Table preservation (TC-0059) | OPEN |

**Phase 4 verdict (R53):** CONDITIONAL_PASS
- FODS: full PASS
- FODT: CONDITIONAL_PASS (3 preservation TCs open)

## Reclassification Path

To achieve Phase 4 PASS for FODT, R54 must close at least TC-0057 (heading preservation).
Full Phase 4 PASS requires all TCs closed.
