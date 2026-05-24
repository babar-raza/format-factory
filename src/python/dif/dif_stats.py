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
