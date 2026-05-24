# R57 Train E — Product Deepening Report

**Sprint:** FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
**Train:** E — Product Deepening
**Date:** 2026-05-23
**Status:** COMPLETE

---

## Summary

Train E adds two new product capabilities to the FODS and FODT parsers: content statistics functions
that enable programmatic document triage and content assessment pipelines. Additionally, a conflicting
wording defect in fods.yaml (IV-R56-010) is repaired.

---

## Deliverable 1 — fods.yaml Wording Fix (IV-R56-010)

**File:** `release-manifests/python-foss/fods.yaml`

**Defect:** The `unsupported_capabilities` list contained "Cell style/formatting preservation",
which conflicted with TC-0055 (style metadata XML passthrough CLOSED in R55).

**Fix:** Changed to "Full visual style fidelity (colors, fonts, borders, column widths round-trip)"
with an inline note clarifying that raw style metadata XML IS preserved verbatim on round-trip
(TC-0055 CLOSED R55) — only visual rendering fidelity is unsupported.

**Also added to `key_capabilities`:**
- "Style metadata XML passthrough: office:automatic-styles + office:styles preserved verbatim on round-trip (R55 TC-0055)"
- "Column definition passthrough: table:table-column elements preserved (R55)"

---

## Deliverable 2 — workbook_stats() for FODS (New Capability)

**File:** `src/python/fods/neutral_model.py`

**Function:** `workbook_stats(workbook: dict[str, Any]) -> dict[str, Any]`

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `sheet_count` | int | Number of sheets |
| `total_rows` | int | Total rows across all sheets |
| `total_cells` | int | Total cells including empty |
| `non_empty_cells` | int | Cells where value is not None |
| `formula_cells` | int | Cells with `table:formula` attribute |
| `per_sheet` | list[dict] | Per-sheet breakdown with all above counts |

**Use case:** Document triage, content assessment pipelines, format conversion pre-screening.

**Tests:** `tests/python/fods/test_r57_fods_stats.py` — 19 tests, all PASS.

---

## Deliverable 3 — document_stats() for FODT (New Capability)

**File:** `src/python/fodt/neutral_model.py`

**Function:** `document_stats(document: dict[str, Any]) -> dict[str, Any]`

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `block_count` | int | Total paragraphs + headings |
| `paragraph_count` | int | Paragraphs only |
| `heading_count` | int | Headings only |
| `list_count` | int | Top-level lists |
| `list_item_count` | int | All items including nested |
| `table_count` | int | Tables |
| `table_cell_count` | int | Total cells across all tables |
| `total_text_length` | int | Sum of text chars across all content |
| `hyperlink_count` | int | Runs with `href` attribute |

**Design note:** When the document has a `content` list (R55 TC-0060 document-order sequence),
statistics are computed from it. Otherwise, the legacy `blocks`/`lists`/`tables` lists are used.

**Tests:** `tests/python/fodt/test_r57_fodt_stats.py` — 25 tests, all PASS.

---

## Test Summary

| File | Tests | Result |
|------|-------|--------|
| `tests/python/fods/test_r57_fods_stats.py` | 19 | PASS |
| `tests/python/fodt/test_r57_fodt_stats.py` | 25 | PASS |
| **Total Train E new tests** | **44** | **PASS** |

---

## Train E Verdict

TRAIN_E_COMPLETE — 3 deliverables shipped; 44 new tests pass; no regressions.
