# R64 Train D — Installed Public API Proof

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Method

1. Created clean venv: `.local/r64-api-smoke-venv/`
2. Installed FODS + FODT wheels from `.local/r64-metadata/package-artifacts/`
3. Imported all public APIs — no source-tree imports

## FODS Public APIs (13 total: 11 R63 + 2 R64)

| # | API | Status |
|---|---|---|
| 1 | workbook_stats | PASS |
| 2 | workbook_type_distribution | PASS |
| 3 | find_sheet_by_name | PASS |
| 4 | workbook_sheet_summary | PASS |
| 5 | workbook_empty_rows | PASS |
| 6 | workbook_formula_list | PASS |
| 7 | workbook_cell_range | PASS |
| 8 | workbook_merged_cell_summary | PASS |
| 9 | workbook_sheet_order | PASS |
| 10 | workbook_numeric_summary | PASS |
| 11 | workbook_column_count | PASS |
| 12 | workbook_row_style_summary | PASS (R64 new) |
| 13 | workbook_formula_edit_policy | PASS (R64 new) |

## FODT Public APIs (13 total: 11 R63 + 2 R64)

| # | API | Status |
|---|---|---|
| 1 | document_stats | PASS |
| 2 | document_heading_outline | PASS |
| 3 | document_text_content | PASS |
| 4 | document_word_count | PASS |
| 5 | document_table_summary | PASS |
| 6 | document_list_stats | PASS |
| 7 | document_reading_level | PASS |
| 8 | document_hyperlink_count | PASS |
| 9 | document_footnote_count | PASS |
| 10 | document_heading_level_distribution | PASS |
| 11 | document_table_cell_count | PASS |
| 12 | document_table_cell_span_summary | PASS (R64 new) |
| 13 | document_text_field_warnings | PASS (R64 new) |

## Verification

```
FODS_INSTALLED_API_SMOKE: PASS (13 APIs)
FODT_INSTALLED_API_SMOKE: PASS (13 APIs)
```

---

INSTALLED_PUBLIC_API_PROOF_STATUS: COMPLETE
