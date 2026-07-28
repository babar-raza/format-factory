"""
TSV row analytics — statistics derived from TSV row and column data.

Extends tabular_document.py with analytics that inspect individual rows and
columns. Uses parse_tsv from tsv_parser.
"""
from __future__ import annotations

from pathlib import Path

from .tsv_parser import parse_tsv

spec_qname = "tsv:tabular-data"
spec_fact_ref = "SAL-TSV-00001"


def tsv_numeric_column_count(source: "str | bytes | Path") -> int:
    """Return count of columns where all non-empty values parse as floats.

    A column is numeric if every data row value, when stripped, is a valid
    float literal.
    """
    result = parse_tsv(source)
    rows = result.get("rows", [])
    headers = result.get("headers", [])
    if not rows or not headers:
        return 0
    col_count = len(headers)
    numeric = 0
    for col_idx in range(col_count):
        col_vals = [r[col_idx] for r in rows if col_idx < len(r)]
        if not col_vals:
            continue
        all_numeric = True
        for v in col_vals:
            v = v.strip()
            if not v:
                continue
            try:
                float(v)
            except ValueError:
                all_numeric = False
                break
        if all_numeric:
            numeric += 1
    return numeric


def tsv_max_row_field_count(source: "str | bytes | Path") -> int:
    """Return the maximum field count observed in any single data row.

    0 if there are no data rows.
    """
    result = parse_tsv(source)
    rows = result.get("rows", [])
    if not rows:
        return 0
    return max(len(r) for r in rows)


def tsv_min_row_field_count(source: "str | bytes | Path") -> int:
    """Return the minimum field count observed in any single data row.

    0 if there are no data rows.
    """
    result = parse_tsv(source)
    rows = result.get("rows", [])
    if not rows:
        return 0
    return min(len(r) for r in rows)


def tsv_has_uniform_row_length(source: "str | bytes | Path") -> bool:
    """Return True if all data rows have the same number of fields.

    True for empty files (vacuously).
    """
    result = parse_tsv(source)
    rows = result.get("rows", [])
    if not rows:
        return True
    lengths = {len(r) for r in rows}
    return len(lengths) == 1


def tsv_empty_cell_count(source: "str | bytes | Path") -> int:
    """Return count of cells (across all data rows) that are empty or whitespace-only."""
    result = parse_tsv(source)
    rows = result.get("rows", [])
    return sum(1 for r in rows for cell in r if not cell.strip())


def tsv_column_unique_value_counts(source: "str | bytes | Path") -> list:
    """Return list of distinct-value counts, one per column in header order.

    Each element is an int — the number of unique stripped values in that column.
    Returns empty list if no headers or rows.
    """
    result = parse_tsv(source)
    headers = result.get("headers", [])
    rows = result.get("rows", [])
    if not headers or not rows:
        return []
    counts = []
    for col_idx in range(len(headers)):
        vals = {r[col_idx].strip() for r in rows if col_idx < len(r)}
        counts.append(len(vals))
    return counts


def tsv_header_names(source: "str | bytes | Path") -> list:
    """Return the list of header names from the TSV file.

    Returns an empty list if the file has no header row or no columns.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("headers") or []


def tsv_first_row_values(source: "str | bytes | Path") -> list:
    """Return the field values of the first data row.

    Returns an empty list if there are no data rows.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    rows = result.get("rows", [])
    return list(rows[0]) if rows else []


def tsv_last_row_values(source: "str | bytes | Path") -> list:
    """Return the field values of the last data row.

    Returns an empty list if there are no data rows.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    rows = result.get("rows", [])
    return list(rows[-1]) if rows else []


def tsv_has_duplicate_headers(source: "str | bytes | Path") -> bool:
    """Return True if any two header names are identical (case-sensitive).

    False when there are no headers or only a single header.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    headers = result.get("headers") or []
    return len(headers) != len(set(headers))


def tsv_all_headers_nonempty(source: "str | bytes | Path") -> bool:
    """Return True if every header name is a non-empty, non-whitespace string.

    Returns True vacuously when there are no headers.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    headers = result.get("headers") or []
    return all(h.strip() for h in headers)


def tsv_is_wide(source: "str | bytes | Path") -> bool:
    """Return True if the file has more columns than data rows.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("column_count", 0) > result.get("row_count", 0)


def tsv_row_count(source: "str | bytes | Path") -> int:
    """Return the number of data rows in the TSV file (excluding header).

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("row_count", 0)


def tsv_column_count(source: "str | bytes | Path") -> int:
    """Return the number of columns in the TSV file.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("column_count", 0)


def tsv_has_rows(source: "str | bytes | Path") -> bool:
    """Return True if the TSV file contains at least one data row.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("row_count", 0) > 0


def tsv_is_single_row(source: "str | bytes | Path") -> bool:
    """Return True if the TSV file contains exactly one data row.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("row_count", 0) == 1


def tsv_header_count(source: "str | bytes | Path") -> int:
    """Return the number of header columns. 0 if no header row.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    headers = result.get("headers") or []
    return len(headers)


def tsv_has_header(source: "str | bytes | Path") -> bool:
    """Return True if the TSV file was parsed as having a header row.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return bool(result.get("has_header", False))


def tsv_first_header(source: "str | bytes | Path") -> str:
    """Return the name of the first header column. Empty string if no headers.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    headers = result.get("headers") or []
    return headers[0] if headers else ""


def tsv_last_header(source: "str | bytes | Path") -> str:
    """Return the name of the last header column. Empty string if no headers.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    headers = result.get("headers") or []
    return headers[-1] if headers else ""


def tsv_is_empty(source: "str | bytes | Path") -> bool:
    """Return True if the TSV file has no rows and no headers.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("row_count", 0) == 0 and not (result.get("headers") or [])


def tsv_total_cells(source: "str | bytes | Path") -> int:
    """Return total cell count (row_count * column_count).

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("row_count", 0) * result.get("column_count", 0)


def tsv_is_tall(source: "str | bytes | Path") -> bool:
    """Return True if row count exceeds column count.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("row_count", 0) > result.get("column_count", 0)


def tsv_delimiter(source: "str | bytes | Path") -> str:
    """Return the delimiter character used in the TSV file.

    Spec: TSV tabular-data (SAL-TSV-00001)
    """
    result = parse_tsv(source)
    return result.get("delimiter", "\t")
