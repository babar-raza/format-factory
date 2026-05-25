# R65 Installed Public API Proof

## FODS (15 public APIs from installed wheel)
workbook_stats, workbook_type_distribution, find_sheet_by_name, workbook_sheet_summary, workbook_empty_rows, workbook_formula_list, workbook_cell_range, workbook_merged_cell_summary, workbook_sheet_order, workbook_numeric_summary, workbook_column_count, workbook_row_style_summary, workbook_formula_edit_policy, workbook_named_range_list, workbook_column_style_summary

## FODT (15 public APIs from installed wheel)
document_stats, document_heading_outline, document_text_content, document_word_count, document_table_summary, document_list_stats, document_reading_level, document_hyperlink_count, document_footnote_count, document_heading_level_distribution, document_table_cell_count, document_table_cell_span_summary, document_text_field_warnings, document_footnote_endnote_summary, document_image_frame_list

## Verification
- Clean venv: .local/r65-api-smoke-venv
- pip install from .local/r65-metadata/package-artifacts/
- import fods; import fodt — both succeed
- All 15+15 APIs present
- INSTALLED_API_SMOKE: PASS

INSTALLED_PUBLIC_API_PROOF_STATUS: COMPLETE
