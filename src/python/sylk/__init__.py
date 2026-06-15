"""
format-factory-sylk — Python FOSS parser for SYLK (Symbolic Link) format.

Public API:
    parse_sylk(file_path)        — returns result dict (never raises)
    parse_sylk_strict(file_path) — raises SylkError subclasses on failure
    probe_sylk(file_path)        — returns header metadata without full parse
    get_capabilities()           — returns capability dict

License: Apache-2.0
Package: format-factory-sylk v0.1.0
Gate history: Gates 1-9 PASSED; Gate 10 R59
"""

from .sylk_parser import (
    parse_sylk,
    parse_sylk_strict,
    probe_sylk,
    get_capabilities,
    sylk_to_csv,
    get_cell_value,
    get_row_values,
    get_column_values,
    get_row_count,
    get_column_count,
    get_cell_count,
    get_all_values,
    set_cell_value,
    write_sylk,
    add_row,
    delete_row,
    count_nonempty_cells,
    sum_column,
    min_column_value,
    max_column_value,
    average_column,
    sylk_to_html,
    find_value,
    count_distinct_values,
    find_rows_by_value,
    sylk_nonempty_rows,
    sylk_numeric_cell_count,
    sylk_string_cell_count,
    sylk_max_column_index,
    sylk_empty_cell_count,
    sylk_row_count,
    sylk_total_sum,
    sylk_column_count,
    SylkError,
    SylkInvalidFormatError,
    SylkSizeError,
    SylkParseError,
    SylkCell,
    SylkDocument,
    sylk_unique_values,
    sylk_cell_type_distribution,
    sylk_has_header,
)

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_sylk",
    "parse_sylk_strict",
    "probe_sylk",
    "get_capabilities",
    "sylk_to_csv",
    "get_cell_value",
    "get_row_values",
    "get_column_values",
    "get_row_count",
    "get_column_count",
    "get_cell_count",
    "get_all_values",
    "set_cell_value",
    "write_sylk",
    "add_row",
    "delete_row",
    "count_nonempty_cells",
    "sum_column",
    "min_column_value",
    "max_column_value",
    "average_column",
    "sylk_to_html",
    "find_value",
    "count_distinct_values",
    "find_rows_by_value",
    "sylk_nonempty_rows",
    "sylk_numeric_cell_count",
    "sylk_string_cell_count",
    "sylk_max_column_index",
    "sylk_empty_cell_count",
    "sylk_row_count",
    "sylk_total_sum",
    "sylk_column_count",
    "SylkError",
    "SylkInvalidFormatError",
    "SylkSizeError",
    "SylkParseError",
    "SylkCell",
    "SylkDocument",
    "sylk_unique_values",
    "sylk_cell_type_distribution",
    "sylk_has_header",
]
