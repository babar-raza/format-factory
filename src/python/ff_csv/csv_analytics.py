"""
CSV extended analytics — supplementary analytics functions.
spec_concept: RFC 4180 CSV structural analytics (field/row metrics, variance, ratios)

Extracted from tabular_document.py to keep it within the 800-LOC policy limit.
All functions here call parse_csv_strict from the core parser.
"""
from __future__ import annotations

from pathlib import Path

from .csv_parser import parse_csv_strict


def csv_total_string_length(file_path: "str | Path") -> int:
    """Return total character count of all cell values combined."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    return sum(len(val) for row in rows for val in row)


def csv_min_row_field_count(file_path: "str | Path") -> int:
    """Return the minimum number of fields in any row. 0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return min(len(row) for row in rows)


def csv_is_square(file_path: "str | Path") -> bool:
    """Return True if row count equals the field count of the first row."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return False
    return len(rows) == len(rows[0])


def csv_column_value_variance(file_path: "str | Path") -> float:
    """Return variance of numeric cell values across all cells. 0.0 if fewer than 2 numeric values."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    nums = []
    for row in rows:
        for val in row:
            v = val.strip()
            if v:
                try:
                    nums.append(float(v))
                except (ValueError, TypeError):
                    pass
    if len(nums) < 2:
        return 0.0
    mean = sum(nums) / len(nums)
    return sum((n - mean) ** 2 for n in nums) / len(nums)


def csv_is_multi_column(file_path: "str | Path") -> bool:
    """Return True if the file has more than one column in any row."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    return any(len(row) > 1 for row in rows)


def csv_field_type_variance(file_path: "str | Path") -> float:
    """Return variance of numeric vs string field counts per row. 0.0 if fewer than 2 rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if len(rows) < 2:
        return 0.0
    numeric_counts = []
    for row in rows:
        nc = 0
        for val in row:
            v = val.strip()
            if v:
                try:
                    float(v)
                    nc += 1
                except (ValueError, TypeError):
                    pass
        numeric_counts.append(nc)
    mean = sum(numeric_counts) / len(numeric_counts)
    return sum((n - mean) ** 2 for n in numeric_counts) / len(numeric_counts)


def csv_header_length_sum(file_path: "str | Path") -> int:
    """Return total character length of all header (first row) fields. 0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return sum(len(field) for field in rows[0])


def csv_row_length_sum(file_path: "str | Path") -> int:
    """Return total character length of all field values across all rows."""
    model = parse_csv_strict(file_path)
    return sum(len(val) for row in model.get("rows", []) for val in row)


def csv_empty_field_ratio(file_path: "str | Path") -> float:
    """Return ratio of empty fields to total fields. 0.0 if no fields."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    total = 0
    empty = 0
    for row in rows:
        for val in row:
            total += 1
            if not val.strip():
                empty += 1
    if total == 0:
        return 0.0
    return empty / total


def csv_string_cell_count(file_path: "str | Path") -> int:
    """Return count of cells with non-numeric string values."""
    model = parse_csv_strict(file_path)
    count = 0
    for row in model.get("rows", []):
        for val in row:
            s = val.strip()
            if s:
                try:
                    float(s)
                except (ValueError, TypeError):
                    count += 1
    return count


def csv_nonempty_row_count(file_path: "str | Path") -> int:
    """Return count of rows that have at least one non-empty field."""
    model = parse_csv_strict(file_path)
    return sum(
        1 for row in model.get("rows", [])
        if any(val.strip() for val in row)
    )


def csv_avg_fields_per_row(file_path: "str | Path") -> float:
    """Return average number of fields per row. 0.0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0.0
    return sum(len(row) for row in rows) / len(rows)


def csv_nonempty_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of non-empty cells to total cells. 0.0 if no cells."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    total = sum(len(row) for row in rows)
    if total == 0:
        return 0.0
    nonempty = sum(1 for row in rows for val in row if val.strip())
    return nonempty / total


def csv_numeric_cell_ratio(file_path: "str | Path") -> float:
    """Return ratio of numeric cells to total cells. 0.0 if no cells."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    total = sum(len(row) for row in rows)
    if total == 0:
        return 0.0
    numeric = 0
    for row in rows:
        for val in row:
            s = val.strip()
            if s:
                try:
                    float(s)
                    numeric += 1
                except (ValueError, TypeError):
                    pass
    return numeric / total


def csv_max_row_length(file_path: "str | Path") -> int:
    """Return the maximum field count observed in any single data row. 0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return max(len(row) for row in rows)


def csv_min_row_length(file_path: "str | Path") -> int:
    """Return the minimum field count observed in any single data row. 0 if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return 0
    return min(len(row) for row in rows)


def csv_has_uniform_row_length(file_path: "str | Path") -> bool:
    """Return True if all data rows have the same number of fields. True if no rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    if not rows:
        return True
    lengths = {len(row) for row in rows}
    return len(lengths) == 1


def csv_column_count(file_path: "str | Path") -> int:
    """Return the number of columns (header fields) in the CSV."""
    model = parse_csv_strict(file_path)
    return model.get("column_count", 0)


def csv_total_cell_count(file_path: "str | Path") -> int:
    """Return total count of cells across all data rows."""
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    return sum(len(row) for row in rows)


def csv_has_header(file_path: "str | Path") -> bool:
    """Return True if the parsed CSV has a header row."""
    model = parse_csv_strict(file_path)
    return bool(model.get("has_header", False))


def csv_header_names(file_path: "str | Path") -> list:
    """Return the list of header names from the CSV file.

    Returns an empty list if the file has no header row or no columns.
    """
    model = parse_csv_strict(file_path)
    return model.get("headers") or []


def csv_first_row_values(file_path: "str | Path") -> list:
    """Return the field values of the first data row.

    Returns an empty list if there are no data rows.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    return list(rows[0]) if rows else []


def csv_last_row_values(file_path: "str | Path") -> list:
    """Return the field values of the last data row.

    Returns an empty list if there are no data rows.
    """
    model = parse_csv_strict(file_path)
    rows = model.get("rows", [])
    return list(rows[-1]) if rows else []


def csv_has_duplicate_headers(file_path: "str | Path") -> bool:
    """Return True if any two header names are identical (case-sensitive).

    False when there are no headers or only a single header.
    """
    model = parse_csv_strict(file_path)
    headers = model.get("headers") or []
    return len(headers) != len(set(headers))


def csv_all_headers_nonempty(file_path: "str | Path") -> bool:
    """Return True if every header name is a non-empty, non-whitespace string.

    Returns True vacuously when there are no headers.
    """
    model = parse_csv_strict(file_path)
    headers = model.get("headers") or []
    return all(h.strip() for h in headers)


def csv_is_wide(file_path: "str | Path") -> bool:
    """Return True if the file has more columns than data rows."""
    model = parse_csv_strict(file_path)
    return model.get("column_count", 0) > model.get("row_count", 0)
