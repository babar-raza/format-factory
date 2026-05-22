# R49 FODS Preservation Matrix

**Sprint:** FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
**Lane:** MT7
**Date:** 2026-05-22

---

## Summary

Preservation matrix for FODS (Flat OpenDocument Spreadsheet) after edit/save/reload cycle.
Assessed for both Python streaming writer and .NET DOM-backed writer.

---

## Cell-Level Preservation

| Attribute | Python writer | .NET writer | Notes |
|-----------|--------------|------------|-------|
| Cell text value | PRESERVED | PRESERVED | Both writers emit/retain the value |
| Cell value_type | PRESERVED | PRESERVED | Python: writes type attr; .NET: DOM pass-through |
| Cell string display | PRESERVED | PRESERVED | Verified in round-trip tests |
| Formula (`table:formula`) | LOST (Python) | PRESERVED (.NET) | Python: value written, formula dropped. Known gap — TC-FORMULA-001 |
| Cell style reference | LOST (Python) | PRESERVED (.NET) | Not in neutral model. Known gap — TC-STYLE-001 |
| Covered cells (`table:covered-table-cell`) | PRESERVED (.NET) | PRESERVED (.NET) | FodsCell.IsCovered tracks this |
| Number of value repetitions | PARTIAL (Python) | PRESERVED (.NET) | table:number-columns-repeated not serialized by Python writer |

---

## Sheet-Level Preservation

| Attribute | Python writer | .NET writer | Notes |
|-----------|--------------|------------|-------|
| Sheet name | PRESERVED | PRESERVED | table:name attribute |
| Sheet count | PRESERVED | PRESERVED | All sheets written |
| Column definitions | LOST (Python) | PRESERVED (.NET) | table:table-column not in neutral model |
| Row height / style | LOST (Python) | PRESERVED (.NET) | Not in neutral model |

---

## Document-Level Preservation

| Attribute | Python writer | .NET writer | Notes |
|-----------|--------------|------------|-------|
| Office metadata (author, date) | LOST (Python) | PRESERVED (.NET) | Python writer doesn't emit meta:document-statistic |
| Named ranges | LOST (Python) | PRESERVED (.NET) | Not parsed into neutral model |
| Styles (fonts, colors) | LOST (Python) | PRESERVED (.NET) | Not in neutral model |
| Scripts / macros | LOST (Python) | PRESERVED (.NET) | Python writer is clean (no macros emitted) |

---

## Preservation Test Coverage

Covered by `tests/python/fods/test_r49_object_model_poc.py`:
- `TestFodsPreservationProof::test_typed_value_preserved_on_other_cells` — typed values survive edit
- `TestFodsPreservationProof::test_multi_row_preservation` — multiple rows preserved
- `TestFodsPythonObjectModelPOC::test_edit_one_cell_preserves_other_cells` — cell preservation
- `TestFodsPythonObjectModelPOC::test_edit_one_cell_preserves_sheet_count` — sheet count

---

## Known Gaps (Taskcards)

| ID | Gap | Priority |
|----|-----|----------|
| TC-FORMULA-001 | FODS Python writer loses formula cells (only value written) | Medium |
| TC-STYLE-001 | FODS Python writer loses cell/row/column styles | Low |
| TC-COLDEF-001 | FODS Python writer loses column definitions | Low |

---

## Verdict

**Python FODS preservation: PARTIAL** — value/type/text preserved; formula/style/column-def lost.
**.NET FODS preservation: FULL** — DOM-backed; all unmodified XML nodes preserved.

For commercial use cases requiring style preservation, the .NET library is the recommended path.
