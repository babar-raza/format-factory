# R66 Installed API and Artifact Replay

## FODS Installed APIs (15 neutral-model)
workbook_stats, workbook_type_distribution, find_sheet_by_name, workbook_sheet_summary,
workbook_empty_rows, workbook_formula_list, workbook_cell_range, workbook_merged_cell_summary,
workbook_sheet_order, workbook_numeric_summary, workbook_column_count, workbook_row_style_summary,
workbook_formula_edit_policy, workbook_named_range_list, workbook_column_style_summary

All 15 callable from clean venv (.local/r66-smoke-venv). No source-tree imports.

## FODT Installed APIs (15 neutral-model)
document_stats, document_heading_outline, document_text_content, document_word_count,
document_table_summary, document_list_stats, document_reading_level, document_hyperlink_count,
document_footnote_count, document_heading_level_distribution, document_table_cell_count,
document_table_cell_span_summary, document_text_field_warnings, document_footnote_endnote_summary,
document_image_frame_list

All 15 callable from clean venv. No source-tree imports.

## Artifacts
- 10 wheels: all present, valid ZIP files
- 10 sdists: all present, valid archives
- 2 nupkgs: FormatFactory.Fods.0.1.0-tier0.nupkg, FormatFactory.Fodt.0.1.0-tier0.nupkg

INSTALLED_API_AND_ARTIFACT_REPLAY: COMPLETE
