"""
format-factory: Gnumeric FOSS Python track.

Minimal FOSS implementation for .gnumeric format support.
Gzip-compressed XML, namespace http://www.gnumeric.org/v10.dtd.
Acquisition Gates 1-7 PASSED.

FOSS track only — no commercial readiness implied.
"""

from .gnumeric_codec import (
    GnumericError,
    GnumericParseError,
    load,
    get_sheet_count,
    get_cell_count,
    extract_values,
    get_sheet_metadata,
    export_to_csv,
    export_to_json,
    probe_gnumeric,
    create_gnumeric,
    write_gnumeric,
    get_cell_value,
    set_cell_value,
    get_sheet_names,
    get_row,
    get_column,
    delete_sheet,
    rename_sheet,
    add_sheet,
    get_sheet_by_name,
    copy_sheet,
    clear_cell,
    get_row_count,
    get_column_count,
    read_cell,
    count_nonempty_cells,
    get_sheet_index,
    sum_column,
    fill_column,
    sum_row,
    get_all_values,
    clear_sheet,
    get_sheet_as_rows,
    fill_row,
    sheet_names,
    row_count,
    get_row_values,
    get_column_values,
)

__all__ = [
    "GnumericError",
    "GnumericParseError",
    "load",
    "get_sheet_count",
    "get_cell_count",
    "extract_values",
    "get_sheet_metadata",
    "export_to_csv",
    "export_to_json",
    "probe_gnumeric",
    "create_gnumeric",
    "write_gnumeric",
    "get_cell_value",
    "set_cell_value",
    "get_sheet_names",
    "get_row",
    "get_column",
    "delete_sheet",
    "rename_sheet",
    "add_sheet",
    "get_sheet_by_name",
    "copy_sheet",
    "clear_cell",
    "get_row_count",
    "get_column_count",
    "read_cell",
    "count_nonempty_cells",
    "get_sheet_index",
    "sum_column",
    "fill_column",
    "sum_row",
    "get_all_values",
    "clear_sheet",
    "get_sheet_as_rows",
    "fill_row",
    "sheet_names",
    "row_count",
    "get_row_values",
    "get_column_values",
]

__version__ = "0.1.0.dev0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"
