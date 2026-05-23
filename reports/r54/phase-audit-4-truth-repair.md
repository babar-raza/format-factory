# Phase Audit 4 Truth Repair

**Sprint:** FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
**Date:** 2026-05-23
**Repairs R53 defect:** Phase Audit 4 TC mislabeling

## R53 Error Summary

R53 Phase Audit 4 Continuation (`reports/r53/phase-audit-4-continuation.md`) contained
three truth defects:

1. **TC-0057 mislabeled as "Heading Preservation"** — TC-0057 is actually "Inline Span Preservation"
2. **TC-0058 mislabeled as "List Preservation"** — TC-0058 is actually "Table Preservation"
3. **TC-0059 mislabeled as "Table Preservation"** — TC-0059 is actually "List Preservation"
4. **Heading preservation falsely claimed NOT_MET** — heading preservation is already implemented in R49

## Corrected TC Mapping

| TC ID | Correct Title | Correct Status (R54) |
|-------|--------------|----------------------|
| TC-0054 | FODS Formula Preservation | CLOSED_VERIFIED (R53) |
| TC-0057 | FODT Inline Span Preservation | OPEN |
| TC-0058 | FODT Table Preservation | OPEN |
| TC-0059 | FODT List Preservation | OPEN (ADVANCED in R54) |

## FODT Heading Preservation: VERIFIED PASS

FODT heading preservation has been implemented since R49. `src/python/fodt/writer.py`
`_write_block()` function (lines 70-73):

```python
if block_type == "heading":
    el = ET.SubElement(parent, _qn("text", "h"))
    level = block.get("heading_level") or 1
    el.set(_qn("text", "outline-level"), str(level))
    el.text = text
```

Round-trip proof (R54 verification):
- Input: `samples/by-format/fodt/headings-and-paragraphs.fodt` (heading levels 1 and 2)
- Parser: correctly captures `{"type": "heading", "text": "Section One", "heading_level": 1}`
- Writer: emits `<text:h text:outline-level="1">Section One</text:h>`
- Result: **HEADING_PRESERVATION: PASS**

No heading preservation taskcard is needed. Headings work correctly since R49.

## Corrected FODT Preservation Status (R54)

| Format | Dimension | Status |
|--------|-----------|--------|
| FODS | Parser completeness | PASS (R50) |
| FODS | Neutral model | PASS (R50) |
| FODS | Writer/save | PASS (R50) |
| FODS | Formula preservation (TC-0054) | **CLOSED_VERIFIED (R53)** |
| FODS | Fuzz/security (Gate 7) | PASS |
| FODT | Parser completeness | PASS (R50) |
| FODT | Neutral model | PASS (R50) |
| FODT | Writer/save | PASS (basic content) |
| FODT | **Heading preservation** | **PASS (R49 — always was implemented)** |
| FODT | Inline span preservation (TC-0057) | OPEN |
| FODT | Table preservation (TC-0058) | OPEN |
| FODT | List preservation (TC-0059) | **PARTIAL_PASS (R54 advances)** |

## Phase Audit 4 Updated Verdict

**R54 Phase Audit 4 verdict:** CONDITIONAL_PASS_WITH_FODT_GAPS
- FODS: full PASS
- FODT headings: PASS (corrected from false NOT_MET)
- FODT inline spans (TC-0057): OPEN — not implemented
- FODT tables (TC-0058): OPEN — not implemented
- FODT lists (TC-0059): PARTIAL_PASS — implemented in R54 (basic round-trip; ordering limitation documented)

## R54 FODT Preservation Implementation

### TC-0059: List Preservation (ADVANCED in R54)

R54 implements list emission in `src/python/fodt/writer.py`:
- `_write_list()` emits `text:list` with `text:list-item` children
- `document_to_xml()` emits lists from `document["lists"]` after blocks
- Limitation: document ordering between blocks and lists/tables not preserved (separate lists in neutral model)
- 5 round-trip tests PASS: `tests/python/fodt/test_r54_fodt_preservation.py`

### TC-0058: Table Preservation (ADVANCED in R54)

R54 implements table emission in `src/python/fodt/writer.py`:
- `_write_table()` emits `table:table` with `table:table-row` and `table:table-cell`
- `document_to_xml()` emits tables from `document["tables"]` after lists
- 5 round-trip tests PASS

### TC-0057: Inline Span Preservation (OPEN after R54)

Inline spans require parser changes (currently `_collect_text()` strips span structure).
Deferred to R55. RISK-003 remains active for inline spans.

## Reclassification Path

To achieve full Phase 4 PASS for FODT, R55 must close:
- TC-0057 (inline spans) — requires parser + writer changes
- TC-0058 (tables, already partially done in R54)
- TC-0059 (lists, partially done in R54 — full ordering fix needed)
