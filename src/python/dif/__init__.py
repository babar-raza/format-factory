"""
format-factory-dif — Python FOSS parser for DIF (Data Interchange Format).

Public API:
    parse_dif(file_path)        — returns result dict (never raises)
    parse_dif_strict(file_path) — raises DifError subclasses on failure
    probe_dif(file_path)        — returns header metadata without full parse
    get_capabilities()          — returns capability dict
    dif_to_csv(file_path)       — export DIF as CSV string (R84 Train N)

License: Apache-2.0
Package: format-factory-dif v0.1.0
Gate history: Gates 1-9 PASSED; Gate 10 R59
"""

from .dif_parser import (
    parse_dif,
    parse_dif_strict,
    probe_dif,
    get_capabilities,
    dif_to_csv,
    write_dif,
    get_cell_value,
    set_cell_value,
    get_row_values,
    get_column_values,
    get_title,
    get_row_count,
    get_column_count,
    count_nonempty_cells,
    total_cell_count,
    get_all_values,
    min_column_value,
    max_column_value,
    sum_column,
    average_column,
    add_row,
    delete_row,
    filter_rows_by_value,
    sum_row,
    sort_rows_by_column,
    get_row_as_dict,
    get_header_info,
    count_distinct_values,
    dif_nonempty_row_count,
    dif_max_row_length,
    dif_string_row_count,
    dif_column_unique_count,
    dif_vectors_count,
    dif_numeric_cell_count,
    dif_total_cell_count,
    DifError,
    DifInvalidFormatError,
    DifSizeError,
    DifCell,
    DifDocument,
)
from .dif_stats import (
    dif_stats,
    dif_numeric_range,
    dif_vector_density,
    dif_string_value_list,
    dif_empty_row_count,
    dif_string_cell_count,
    dif_total_numeric_count,
)

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_dif",
    "parse_dif_strict",
    "probe_dif",
    "get_capabilities",
    "dif_to_csv",
    "write_dif",
    "get_cell_value",
    "set_cell_value",
    "get_row_values",
    "get_column_values",
    "get_title",
    "get_row_count",
    "get_column_count",
    "count_nonempty_cells",
    "total_cell_count",
    "get_all_values",
    "min_column_value",
    "max_column_value",
    "sum_column",
    "average_column",
    "add_row",
    "delete_row",
    "filter_rows_by_value",
    "sum_row",
    "sort_rows_by_column",
    "get_row_as_dict",
    "get_header_info",
    "count_distinct_values",
    "dif_nonempty_row_count",
    "dif_max_row_length",
    "dif_string_row_count",
    "dif_column_unique_count",
    "dif_vectors_count",
    "dif_numeric_cell_count",
    "dif_total_cell_count",
    "DifError",
    "DifInvalidFormatError",
    "DifSizeError",
    "DifCell",
    "DifDocument",
    "dif_stats",
    "dif_numeric_range",
    "dif_vector_density",
    "dif_string_value_list",
    "dif_empty_row_count",
    "dif_string_cell_count",
    "dif_total_numeric_count",
]
