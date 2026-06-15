"""
format-factory-fods -- Python FOSS parser/writer for OpenDocument Flat Spreadsheet (FODS).

Public API:
    parse_fods(file_path)              -- streaming parser, never raises
    parse_fods_strict(file_path)       -- raises FodsError subclasses on failure
    write_fods(workbook, path)         -- serialize neutral model workbook to FODS file
    workbook_to_xml(workbook)          -- serialize neutral model workbook to XML string
    workbook_stats(workbook)           -- return cell-level statistics dict (R57/R58)
    workbook_type_distribution(wb)     -- distribution of cell value types (R59)
    find_sheet_by_name(wb, name)       -- return sheet dict by name or None (R59)
    workbook_sheet_summary(wb)         -- compact per-sheet summary list (R60)
    workbook_empty_rows(wb)            -- empty-row statistics (R60)
    workbook_formula_list(wb)          -- flat list of all formula cells (R61)
    workbook_cell_range(wb, ...)       -- 2D slice of cell values (R61)
    workbook_merged_cell_summary(wb)   -- merged-cell annotations (R62)
    workbook_sheet_order(wb)           -- ordered list of sheet names (R62)
    workbook_row_style_summary(wb)    -- row style attributes per sheet (R64)
    workbook_formula_edit_policy(wb)  -- formula edit/lock policy counts (R64)
    workbook_named_range_list(wb)     -- list of defined named ranges (R65)
    workbook_column_style_summary(wb) -- column style attributes per sheet (R65)
    workbook_style_family_list(wb)    -- style family inventory (R66)
    workbook_data_validation_summary(wb) -- data validation summary (R66)
    workbook_column_width_summary(wb) -- column width data per sheet (R75)
    workbook_cell_type_matrix(wb)     -- cell type distribution per sheet (R75)
    workbook_set_cell_value(wb, sheet, row, col, value) -- edit a cell value (R76)
    workbook_warnings_for_unsupported_edit(wb, sheet, row, col) -- edit safety warnings (R76)

License: Apache-2.0
Package: format-factory-fods v0.1.0
Gate history: Gates 1-10 PASSED (2026-05-08)
R46 MT6: write_fods / workbook_to_xml added (alpha-foss-preview write capability)
R57/R58: workbook_stats() exposed in public API
R61: workbook_formula_list, workbook_cell_range added
R62: workbook_merged_cell_summary, workbook_sheet_order added
R63: all 9 workbook APIs exported at package level (IV-R62-002 repair)
"""

from .parser import parse_fods, parse_fods_strict
from .writer import write_fods, workbook_to_xml
from .neutral_model import (
    workbook_stats,
    workbook_type_distribution,
    find_sheet_by_name,
    workbook_sheet_summary,
    workbook_empty_rows,
    workbook_formula_list,
    workbook_cell_range,
    workbook_merged_cell_summary,
    workbook_sheet_order,
    workbook_numeric_summary,
    workbook_column_count,
    workbook_row_style_summary,
    workbook_formula_edit_policy,
    workbook_named_range_list,
    workbook_column_style_summary,
    workbook_style_family_list,
    workbook_data_validation_summary,
    workbook_column_width_summary,
    workbook_cell_type_matrix,
    workbook_set_cell_value,
    workbook_warnings_for_unsupported_edit,
    workbook_add_sheet,
    workbook_rename_sheet,
    workbook_remove_sheet,
    workbook_to_csv,
    workbook_get_cell_value,
    workbook_find_cells,
    workbook_count_matching_cells,
    workbook_to_html,
    workbook_get_column_values,
    workbook_count_nonempty_cells,
    workbook_max_column_count,
    workbook_numeric_density,
    workbook_total_numeric_value,
    fods_sheet_count,
    fods_total_cell_count,
    workbook_row_count,
    workbook_cell_text_at,
)
from .exceptions import FodsError, FodsInputError, FodsSizeError, FodsParseError
from .constants import FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION, MAX_FILE_BYTES

__version__ = PACKAGE_VERSION
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_fods",
    "parse_fods_strict",
    "write_fods",
    "workbook_to_xml",
    "workbook_stats",
    "workbook_type_distribution",
    "find_sheet_by_name",
    "workbook_sheet_summary",
    "workbook_empty_rows",
    "workbook_formula_list",
    "workbook_cell_range",
    "workbook_merged_cell_summary",
    "workbook_sheet_order",
    "workbook_numeric_summary",
    "workbook_column_count",
    "workbook_row_style_summary",
    "workbook_formula_edit_policy",
    "workbook_named_range_list",
    "workbook_column_style_summary",
    "workbook_style_family_list",
    "workbook_data_validation_summary",
    "workbook_column_width_summary",
    "workbook_cell_type_matrix",
    "workbook_set_cell_value",
    "workbook_warnings_for_unsupported_edit",
    "workbook_add_sheet",
    "workbook_rename_sheet",
    "workbook_remove_sheet",
    "workbook_to_csv",
    "workbook_get_cell_value",
    "workbook_find_cells",
    "workbook_count_matching_cells",
    "workbook_to_html",
    "workbook_get_column_values",
    "workbook_count_nonempty_cells",
    "workbook_max_column_count",
    "workbook_numeric_density",
    "workbook_total_numeric_value",
    "fods_sheet_count",
    "fods_total_cell_count",
    "workbook_row_count",
    "workbook_cell_text_at",
    "FodsError",
    "FodsInputError",
    "FodsSizeError",
    "FodsParseError",
    "FORMAT_ID",
    "SPEC_VERSION",
    "PACKAGE_VERSION",
    "MAX_FILE_BYTES",
]
