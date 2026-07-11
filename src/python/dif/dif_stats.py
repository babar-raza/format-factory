"""
dif_stats.py -- Statistics and analysis functions for DIF neutral model dicts.

Works on the dict output of parse_dif(), not on file paths.
All functions are pure: no I/O, no mutation.

Added in R62 (format track advancement).

License: Apache-2.0
Package: format-factory-dif v0.1.0
"""
from __future__ import annotations

from typing import Any


def dif_stats(dif_doc: dict[str, Any]) -> dict[str, Any]:
    """Return aggregate statistics for a DIF spreadsheet dict.

    Works on the output of parse_dif().
    Returns:
        row_count (int), vectors (int), tuples (int),
        total_cells (int), numeric_cells (int), string_cells (int),
        empty_cells (int), title (str).
    """
    rows = dif_doc.get("rows", [])
    vectors = dif_doc.get("vectors", 0)
    tuples_ = dif_doc.get("tuples", 0)
    title = dif_doc.get("title", "")

    total_cells = 0
    numeric_cells = 0
    string_cells = 0
    empty_cells = 0

    for row in rows:
        for cell in row:
            total_cells += 1
            cell_type = cell.get("type", "")
            val = cell.get("value")
            if cell_type in ("numeric", "number") or isinstance(val, (int, float)):
                numeric_cells += 1
            elif cell_type in ("string", "text") and val not in (None, ""):
                string_cells += 1
            elif val in (None, ""):
                empty_cells += 1
            else:
                string_cells += 1

    return {
        "row_count": len(rows),
        "vectors": vectors,
        "tuples": tuples_,
        "total_cells": total_cells,
        "numeric_cells": numeric_cells,
        "string_cells": string_cells,
        "empty_cells": empty_cells,
        "title": title,
    }


def dif_numeric_range(dif_doc: dict[str, Any]) -> dict[str, Any]:
    """Return the min/max numeric values found in a DIF document dict.

    Returns: min_value (float | None), max_value (float | None),
             numeric_count (int).
    """
    rows = dif_doc.get("rows", [])
    values: list[float] = []

    for row in rows:
        for cell in row:
            val = cell.get("value")
            cell_type = cell.get("type", "")
            if cell_type in ("numeric", "number") or isinstance(val, (int, float)):
                try:
                    values.append(float(val))
                except (TypeError, ValueError):
                    pass

    if not values:
        return {"min_value": None, "max_value": None, "numeric_count": 0}
    return {
        "min_value": min(values),
        "max_value": max(values),
        "numeric_count": len(values),
    }


def dif_vector_density(dif_doc: dict) -> dict:
    """Return density statistics for DIF vectors (rows).

    Each DIF vector (row) contains one or more tuples (cells). This function
    measures the density — how many cells per vector are non-empty. Returns:
      total_vectors: int
      total_tuples: int
      non_empty_tuples: int
      density: float             — non_empty_tuples / total_tuples
      avg_tuples_per_vector: float

    """
    vectors = dif_doc.get("vectors", [])
    total_tuples = 0
    non_empty = 0
    for vec in vectors:
        tuples = vec.get("tuples", []) if isinstance(vec, dict) else []
        for tup in tuples:
            total_tuples += 1
            val = tup.get("value") if isinstance(tup, dict) else tup
            if val is not None and val != "" and val != 0:
                non_empty += 1
    total_vecs = len(vectors)
    return {
        "total_vectors": total_vecs,
        "total_tuples": total_tuples,
        "non_empty_tuples": non_empty,
        "density": round(non_empty / total_tuples, 4) if total_tuples > 0 else 0.0,
        "avg_tuples_per_vector": round(total_tuples / total_vecs, 2) if total_vecs > 0 else 0.0,
    }


def dif_string_value_list(dif_doc: dict[str, Any]) -> list[str]:
    """Return all string cell values found in the DIF document.

    Scans all rows for cells with type 'string' or 'text' and collects
    their values into a flat list. Useful for text extraction and
    content inventory of DIF files.

    Returns:
        list[str] — all string values in row-major order. Empty list if none.

    """
    result: list[str] = []
    for row in dif_doc.get("rows", []):
        for cell in row:
            cell_type = cell.get("type", "")
            val = cell.get("value")
            if cell_type in ("string", "text") and val is not None and val != "":
                result.append(str(val))
    return result


def dif_empty_row_count(dif_doc: dict[str, Any]) -> int:
    """Return the count of rows where all cells are empty in a DIF document.

    A cell is considered empty if its value is None or empty string "".

    Args:
        dif_doc: Parsed DIF document dict (from parse_dif()).

    Returns:
        int — number of fully-empty rows. 0 if no rows or no empty rows.

    Useful for data quality assessment and sparse-data detection in DIF files.
    """
    count = 0
    for row in dif_doc.get("rows", []):
        if all(
            cell.get("value") in (None, "")
            for cell in row
        ) if row else True:
            count += 1
    return count


def dif_string_cell_count(dif_doc: dict[str, Any]) -> int:
    """Return the count of string-type cells in the DIF document.

    Scans all rows for cells with type 'string' or 'text' that have a
    non-empty value. This is a simpler alternative to dif_string_value_list()
    when only the count is needed.

    Args:
        dif_doc: Parsed DIF document dict (from parse_dif()).

    Returns:
        int -- number of string cells found. 0 if none.

    Useful for content type assessment and format triage.
    """
    count = 0
    for row in dif_doc.get("rows", []):
        for cell in row:
            cell_type = cell.get("type", "")
            val = cell.get("value")
            if cell_type in ("string", "text") and val is not None and val != "":
                count += 1
    return count


def dif_total_numeric_count(dif_doc: dict[str, Any]) -> int:
    """Return the total count of numeric-type cells in the DIF document.

    Scans all rows for cells whose type is 'numeric' or 'number', or whose
    value is an int or float. Complements dif_string_cell_count() for a
    complete numeric/string/empty breakdown without requiring the full
    dif_stats() aggregation.

    Args:
        dif_doc: Parsed DIF document dict (from parse_dif()).

    Returns:
        int — total number of numeric cells. 0 if none.
    """
    count = 0
    for row in dif_doc.get("rows", []):
        for cell in row:
            cell_type = cell.get("type", "")
            val = cell.get("value")
            if cell_type in ("numeric", "number") or isinstance(val, (int, float)):
                count += 1
    return count


# ---------------------------------------------------------------------------
# File-path analytics functions for deepening tests (TC-F-012)
# ---------------------------------------------------------------------------
from pathlib import Path as _Path


def dif_max_row_width(file_path: "str | _Path") -> int:
    """Return the maximum number of cells in any row. 0 if no rows."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    if not doc.rows:
        return 0
    return max(len(row) for row in doc.rows)


def dif_empty_cell_ratio(file_path: "str | _Path") -> float:
    """Return ratio of cells with None/empty value to total cells. 0.0 if no cells."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    total = sum(len(row) for row in doc.rows)
    if total == 0:
        return 0.0
    empty = sum(
        1 for row in doc.rows for cell in row
        if cell.value is None or (isinstance(cell.value, str) and not cell.value.strip())
    )
    return float(empty) / total


def dif_string_cell_total_length(file_path: "str | _Path") -> int:
    """Return total character length of all string-type cell values."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    total = 0
    for row in doc.rows:
        for cell in row:
            if cell.value_type == 'string' and cell.value is not None:
                total += len(str(cell.value))
    return total


def dif_numeric_value_total(file_path: "str | _Path") -> float:
    """Return sum of all numeric cell values. 0.0 if no numeric cells."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    total = 0.0
    for row in doc.rows:
        for cell in row:
            if cell.value_type == 'numeric' and cell.value is not None:
                try:
                    total += float(cell.value)
                except (ValueError, TypeError):
                    pass
    return total


# ---------------------------------------------------------------------------
# Spec-backed analytics: DIF-FACT-001, DIF-FACT-002 (TC-SR-004)
# ---------------------------------------------------------------------------


def dif_declared_vector_count(file_path: "str | _Path") -> int:
    """Return the VECTORS header value — the declared column count.

    Grounded in DIF-FACT-001: DIF files start with a header section containing
    TABLE, VECTORS, and TUPLES directives that define the document dimensions.
    The VECTORS directive specifies the number of columns declared by the author
    of the file, which may differ from the actual data row width.

    Args:
        file_path: Path to a DIF file.

    Returns:
        int — declared VECTORS count (0 if header is missing or 0).
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return doc.vectors


def dif_declared_tuple_count(file_path: "str | _Path") -> int:
    """Return the TUPLES header value — the declared row count.

    Grounded in DIF-FACT-001: DIF files start with a header section containing
    TABLE, VECTORS, and TUPLES directives that define the document dimensions.
    The TUPLES directive specifies the number of rows declared in the header,
    which may differ from the actual parsed row count.

    Args:
        file_path: Path to a DIF file.

    Returns:
        int — declared TUPLES count (0 if header is missing or 0).
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return doc.tuples


def dif_has_title(file_path: "str | _Path") -> bool:
    """Return True if the DIF file TABLE header contains a non-empty title.

    Grounded in DIF-FACT-001: DIF files start with a header section containing
    TABLE, VECTORS, and TUPLES directives. The TABLE directive carries the
    document title as its string argument (may be empty string in minimal files).

    Args:
        file_path: Path to a DIF file.

    Returns:
        bool — True if the TABLE title string is non-empty, False otherwise.
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return bool(doc.title and doc.title.strip())


def dif_boolean_cell_count(file_path: "str | _Path") -> int:
    """Return the count of boolean-typed cells in the DIF file.

    Grounded in DIF-FACT-002: the DATA section contains cell values where
    each cell has a type indicator. Boolean values (TRUE/FALSE markers after
    type 0 indicators with V marker) are parsed as value_type='boolean'.

    Args:
        file_path: Path to a DIF file.

    Returns:
        int — number of boolean cells. 0 if none.
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return sum(
        1 for row in doc.rows for cell in row
        if cell.value_type == 'boolean'
    )


def dif_special_cell_count(file_path: "str | _Path") -> int:
    """Return the count of special/NA cells in the DIF file.

    Grounded in DIF-FACT-002: the DATA section uses special markers for
    non-numeric, non-string values. Cells with value_type='special' include
    NA (not available) and other V-marker variants that do not resolve to
    numeric or string values.

    Args:
        file_path: Path to a DIF file.

    Returns:
        int — number of special/NA cells. 0 if none.
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return sum(
        1 for row in doc.rows for cell in row
        if cell.value_type == 'special'
    )


def dif_total_cell_count(file_path: "str | _Path") -> int:
    """Return the total count of cells across all data rows in the DIF file."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return sum(len(row) for row in doc.rows)


def dif_min_row_width(file_path: "str | _Path") -> int:
    """Return the minimum cell count in any single row. 0 if no rows."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    if not doc.rows:
        return 0
    return min(len(row) for row in doc.rows)


def dif_has_string_cells(file_path: "str | _Path") -> bool:
    """Return True if any cell in the DIF file has value_type='string'."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return any(
        cell.value_type == 'string'
        for row in doc.rows for cell in row
    )


def dif_file_numeric_cell_count(file_path: "str | _Path") -> int:
    """Return count of cells with value_type='numeric' in the DIF file."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return sum(
        1 for row in doc.rows for cell in row
        if cell.value_type == 'numeric'
    )


def dif_title_length(file_path: "str | _Path") -> int:
    """Return character length of the DIF document title. 0 if no title."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return len(doc.title) if doc.title else 0


def dif_all_cells_numeric(file_path: "str | _Path") -> bool:
    """Return True if every cell in every data row is numeric. True if no rows."""
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    if not doc.rows:
        return True
    return all(
        cell.value_type == 'numeric'
        for row in doc.rows for cell in row
    )


def dif_title(file_path: "str | _Path") -> str:
    """Return the document title string, or empty string if not set.

    Spec: DIF TABLE header directive (FACT-DIF-001)
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return doc.title or ""


def dif_row_count(file_path: "str | _Path") -> int:
    """Return the number of data rows in the DIF document.

    Spec: DIF TABLE row structure (FACT-DIF-001)
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return len(doc.rows)


def dif_first_row_cell_count(file_path: "str | _Path") -> int:
    """Return the cell count in the first data row. 0 if no rows.

    Spec: DIF TABLE row structure (FACT-DIF-001)
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return len(doc.rows[0]) if doc.rows else 0


def dif_has_numeric_cells(file_path: "str | _Path") -> bool:
    """Return True if any cell in the document has value_type 'numeric'.

    Spec: DIF numeric value type (FACT-DIF-001)
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return any(
        cell.value_type == 'numeric'
        for row in doc.rows for cell in row
    )


def dif_numeric_cell_values(file_path: "str | _Path") -> list:
    """Return list of float values from all numeric cells, in row-major order.

    Spec: DIF numeric value type (FACT-DIF-001)
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return [
        float(cell.value)
        for row in doc.rows for cell in row
        if cell.value_type == 'numeric' and cell.value is not None
    ]


def dif_cell_type_set(file_path: "str | _Path") -> list:
    """Return sorted list of distinct cell value_type strings across all rows.

    Spec: DIF cell type taxonomy (FACT-DIF-001)
    """
    from .dif_parser import parse_dif_strict as _parse
    doc = _parse(file_path)
    return sorted({cell.value_type for row in doc.rows for cell in row})
