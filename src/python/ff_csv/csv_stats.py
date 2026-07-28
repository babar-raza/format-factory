"""
csv_stats.py -- Statistics and analysis functions for CSV neutral model dicts.

Works on the dict output of parse_csv(), not on file paths.
All functions are pure: no I/O, no mutation.

Added in R62 (format track advancement).

License: Apache-2.0
Package: format-factory-csv v0.1.0
"""
from __future__ import annotations

from typing import Any


def table_stats(csv_doc: dict[str, Any]) -> dict[str, Any]:
    """Return aggregate statistics for a CSV table dict.

    Works on the output of parse_csv() / parse_csv_strict().
    Returns:
        row_count (int), column_count (int), has_header (bool),
        header_names (list[str] | None), non_empty_cells (int),
        total_cells (int), empty_cell_count (int).
    """
    rows = csv_doc.get("rows", [])
    headers = csv_doc.get("headers")
    column_count = csv_doc.get("column_count", 0)

    total_cells = 0
    non_empty_cells = 0
    for row in rows:
        for cell in row:
            total_cells += 1
            if str(cell).strip():
                non_empty_cells += 1

    empty_cell_count = total_cells - non_empty_cells

    return {
        "row_count": len(rows),
        "column_count": column_count,
        "has_header": bool(csv_doc.get("has_header", False)),
        "header_names": list(headers) if headers else None,
        "total_cells": total_cells,
        "non_empty_cells": non_empty_cells,
        "empty_cell_count": empty_cell_count,
        "delimiter": csv_doc.get("delimiter", ","),
    }


def column_value_counts(csv_doc: dict[str, Any], column_index: int) -> dict[str, int]:
    """Count distinct values in a specific column of a CSV table dict.

    Returns a dict mapping value string → count.
    Empty cells are counted as empty string key "".
    """
    rows = csv_doc.get("rows", [])
    counts: dict[str, int] = {}
    for row in rows:
        if column_index < len(row):
            val = str(row[column_index]).strip()
        else:
            val = ""
        counts[val] = counts.get(val, 0) + 1
    return counts


def csv_row_length_distribution(csv_doc: dict) -> dict:
    """Return distribution of row lengths (column counts) across the CSV.

    Counts how many rows have each distinct column count. Returns:
      by_length: dict[int, int]  — {column_count: row_count}
      min_length: int | None
      max_length: int | None
      is_uniform: bool           — True if all rows have same length
      total_rows: int

    """
    rows = csv_doc.get("rows", [])
    by_length: dict[int, int] = {}
    for row in rows:
        length = len(row) if isinstance(row, (list, tuple)) else 0
        by_length[length] = by_length.get(length, 0) + 1
    lengths = list(by_length.keys())
    return {
        "by_length": by_length,
        "min_length": min(lengths) if lengths else None,
        "max_length": max(lengths) if lengths else None,
        "is_uniform": len(lengths) <= 1,
        "total_rows": len(rows),
    }


def csv_field_type_summary(rows: list) -> dict[str, int]:
    """Return counts of numeric, empty, and text fields across all rows.

    Scans every field in every row and classifies it:
      - 'numeric': the string representation can be parsed as int or float
      - 'empty': the field is None or an empty/whitespace-only string
      - 'text': everything else

    Args:
        rows: list of lists (each inner list is a row of field values).

    Returns:
        dict with keys 'numeric', 'empty', 'text' mapping to int counts.

    """
    counts: dict[str, int] = {"numeric": 0, "empty": 0, "text": 0}
    for row in rows:
        if not isinstance(row, (list, tuple)):
            continue
        for field in row:
            if field is None or (isinstance(field, str) and not field.strip()):
                counts["empty"] += 1
            else:
                s = str(field).strip()
                try:
                    float(s)
                    counts["numeric"] += 1
                except (ValueError, TypeError):
                    counts["text"] += 1
    return counts


def csv_empty_row_count(rows: list) -> int:
    """Return the count of rows where all fields are empty.

    A field is considered empty if it is None or an empty/whitespace-only string.

    Args:
        rows: list of lists (each inner list is a row of field values).

    Returns:
        int — number of fully-empty rows. 0 if no rows or no empty rows.

    Useful for data quality assessment and sparse-data detection in CSV files.
    """
    count = 0
    for row in rows:
        if not isinstance(row, (list, tuple)):
            count += 1
            continue
        if not row:
            count += 1
            continue
        if all(
            field is None or (isinstance(field, str) and not field.strip())
            for field in row
        ):
            count += 1
    return count


def csv_max_field_length(rows: list) -> int:
    """Return the maximum field length (character count) across all rows.

    Scans every field in every row and returns the length of the longest
    field value (as a string). Useful for detecting oversized fields,
    column width estimation, and data quality checks.

    Args:
        rows: list of lists (each inner list is a row of field values).

    Returns:
        int -- maximum field length in characters. 0 if no fields or empty rows.

    """
    max_len = 0
    for row in rows:
        if not isinstance(row, (list, tuple)):
            continue
        for field in row:
            if field is None:
                continue
            field_len = len(str(field))
            if field_len > max_len:
                max_len = field_len
    return max_len


def csv_header_count(csv_doc: dict[str, Any]) -> int:
    """Return count of header columns. 0 if no header row.

    Args:
        csv_doc: dict output of parse_csv() / parse_csv_strict().

    Returns:
        int — number of header columns.
    """
    headers = csv_doc.get("headers")
    return len(headers) if headers else 0


def csv_has_headers(csv_doc: dict[str, Any]) -> bool:
    """Return True if the CSV document was parsed as having a header row.

    Args:
        csv_doc: dict output of parse_csv() / parse_csv_strict().

    Returns:
        bool — True if has_header is set.
    """
    return bool(csv_doc.get("has_header", False))


def csv_first_row(csv_doc: dict[str, Any]) -> list:
    """Return the first data row as a list of values. Empty list if no rows.

    Args:
        csv_doc: dict output of parse_csv() / parse_csv_strict().

    Returns:
        list — first data row, or [].
    """
    rows = csv_doc.get("rows", [])
    return list(rows[0]) if rows else []


def csv_last_row(csv_doc: dict[str, Any]) -> list:
    """Return the last data row as a list of values. Empty list if no rows.

    Args:
        csv_doc: dict output of parse_csv() / parse_csv_strict().

    Returns:
        list — last data row, or [].
    """
    rows = csv_doc.get("rows", [])
    return list(rows[-1]) if rows else []


def csv_is_square(csv_doc: dict[str, Any]) -> bool:
    """Return True if row count equals column count.

    Args:
        csv_doc: dict output of parse_csv() / parse_csv_strict().

    Returns:
        bool — True if len(rows) == column_count.
    """
    rows = csv_doc.get("rows", [])
    col_count = csv_doc.get("column_count", 0)
    return len(rows) == col_count


def csv_is_tall(csv_doc: dict[str, Any]) -> bool:
    """Return True if row count exceeds column count.

    Args:
        csv_doc: dict output of parse_csv() / parse_csv_strict().

    Returns:
        bool — True if len(rows) > column_count.
    """
    rows = csv_doc.get("rows", [])
    col_count = csv_doc.get("column_count", 0)
    return len(rows) > col_count


def csv_row_count(csv_doc: dict[str, Any]) -> int:
    """Return the number of data rows in the CSV document.

    Args:
        csv_doc: dict output of parse_csv().

    Returns:
        int — row count (not including header row).
    """
    return csv_doc.get("row_count", 0)


def csv_column_count(csv_doc: dict[str, Any]) -> int:
    """Return the number of columns in the CSV document.

    Args:
        csv_doc: dict output of parse_csv().

    Returns:
        int — column count.
    """
    return csv_doc.get("column_count", 0)


def csv_delimiter(csv_doc: dict[str, Any]) -> str:
    """Return the field delimiter character used in the CSV document.

    Args:
        csv_doc: dict output of parse_csv().

    Returns:
        str — delimiter (e.g. ',' or '\t').
    """
    return csv_doc.get("delimiter", ",")


def csv_is_empty(csv_doc: dict[str, Any]) -> bool:
    """Return True if the CSV document has no rows and no headers.

    Args:
        csv_doc: dict output of parse_csv().

    Returns:
        bool — True if both row_count == 0 and headers is empty.
    """
    return csv_doc.get("row_count", 0) == 0 and not csv_doc.get("headers", [])


def csv_has_data_rows(csv_doc: dict[str, Any]) -> bool:
    """Return True if the CSV document has at least one data row.

    Args:
        csv_doc: dict output of parse_csv().

    Returns:
        bool — True if row_count > 0.
    """
    return csv_doc.get("row_count", 0) > 0


def csv_first_header(csv_doc: dict[str, Any]) -> str:
    """Return the name of the first header column. Empty string if no headers.

    Args:
        csv_doc: dict output of parse_csv().

    Returns:
        str — first header string, or '' if headers is empty.
    """
    headers = csv_doc.get("headers", [])
    return headers[0] if headers else ""
