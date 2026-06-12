"""
format-factory-csv — Minimal FOSS CSV parser (Gate 4 prototype).

RFC 4180 comma-separated values parser using Python stdlib csv module.

publication_authorized: false
commercial_product_ready: false
capability_level: alpha-foss-preview
track: python-foss

Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""

from .csv_parser import (
    parse_csv,
    parse_csv_strict,
    probe_csv,
    get_capabilities,
    get_row_count,
    get_column_names,
    get_cell_value,
    csv_column_count,
    csv_has_header,
    csv_numeric_row_count,
    count_distinct_values,
    CsvError,
    CsvInputError,
    CsvSizeError,
    CsvParseError,
)
from .csv_writer import (
    write_csv,
    write_csv_to_file,
    parse_and_rewrite,
    CsvWriteError,
)
from .csv_stats import (
    table_stats,
    column_value_counts,
    csv_row_length_distribution,
    csv_field_type_summary,
    csv_empty_row_count,
    csv_max_field_length,
)

__version__ = "0.1.0"
__track__ = "python-foss"
__commercial_ready__ = False
__capability_level__ = "alpha-foss-preview"

__all__ = [
    "parse_csv",
    "parse_csv_strict",
    "probe_csv",
    "get_capabilities",
    "get_row_count",
    "get_column_names",
    "get_cell_value",
    "csv_column_count",
    "csv_has_header",
    "csv_numeric_row_count",
    "count_distinct_values",
    "CsvError",
    "CsvInputError",
    "CsvSizeError",
    "CsvParseError",
    "table_stats",
    "column_value_counts",
    "csv_row_length_distribution",
    "csv_field_type_summary",
    "csv_empty_row_count",
    "csv_max_field_length",
    "write_csv",
    "write_csv_to_file",
    "parse_and_rewrite",
    "CsvWriteError",
]
