"""
csv_stats.py -- Statistics and analysis functions for CSV neutral model dicts.

Works on the dict output of parse_csv(), not on file paths.
All functions are pure: no I/O, no mutation.

Added in R62 Train I (format track advancement).

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
    Added in R62 Train I.
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
    Added in R62 Train I.
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
