"""
dif_stats.py -- Statistics and analysis functions for DIF neutral model dicts.

Works on the dict output of parse_dif(), not on file paths.
All functions are pure: no I/O, no mutation.

Added in R62 Train I (format track advancement).

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
    Added in R62 Train I.
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
    Added in R62 Train I.
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

    Added in R63 Train I (DIF format track advancement).
    """
    from typing import Any
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

    Added in R64 Train I (DIF format track advancement).
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
    Added in R65 Train I (DIF format track advancement).
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
    Added in R66 Train I (DIF format track advancement).
    """
    count = 0
    for row in dif_doc.get("rows", []):
        for cell in row:
            cell_type = cell.get("type", "")
            val = cell.get("value")
            if cell_type in ("string", "text") and val is not None and val != "":
                count += 1
    return count
