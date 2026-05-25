"""
ods_stats.py -- Statistics and analysis functions for ODS neutral model dicts.

Works on the dict output of parse_ods(), not on file paths.
All functions are pure: no I/O, no mutation.

Added in R62 Train I (format track advancement).

License: Apache-2.0
Package: format-factory-ods v0.1.0
"""
from __future__ import annotations

from typing import Any


def spreadsheet_stats(ods_doc: dict[str, Any]) -> dict[str, Any]:
    """Return aggregate statistics for an ODS spreadsheet dict.

    Works on the output of parse_ods().
    Returns:
        sheet_count (int), total_rows (int), total_cells (int),
        non_empty_cells (int), per_sheet (list[dict]).
    Added in R62 Train I.
    """
    sheets = ods_doc.get("sheets", [])
    total_rows = 0
    total_cells = 0
    non_empty_cells = 0
    per_sheet: list[dict[str, Any]] = []

    for sheet in sheets:
        s_rows = sheet.get("rows", [])
        s_cells = 0
        s_non_empty = 0
        for row in s_rows:
            cells = row.get("cells", [])
            s_cells += len(cells)
            for cell in cells:
                val = cell.get("value") or cell.get("text") or ""
                if val not in (None, "", 0) or str(val).strip():
                    s_non_empty += 1
        total_rows += len(s_rows)
        total_cells += s_cells
        non_empty_cells += s_non_empty
        per_sheet.append({
            "name": sheet.get("name", ""),
            "row_count": len(s_rows),
            "cell_count": s_cells,
            "non_empty_cells": s_non_empty,
        })

    return {
        "sheet_count": len(sheets),
        "total_rows": total_rows,
        "total_cells": total_cells,
        "non_empty_cells": non_empty_cells,
        "per_sheet": per_sheet,
    }


def sheet_name_order(ods_doc: dict[str, Any]) -> list[str]:
    """Return the ordered list of sheet names from an ODS document dict.

    Added in R62 Train I.
    """
    return [
        sheet.get("name", f"Sheet{i + 1}")
        for i, sheet in enumerate(ods_doc.get("sheets", []))
    ]


def ods_cell_type_distribution(ods_doc: dict) -> dict:
    """Return distribution of cell value types across the ODS document.

    Scans all cells and classifies each by whether it has text, a numeric
    value, is empty, or carries other content. Returns:
      by_type: dict[str, int]   — count per type label
      total_cells: int
      empty_fraction: float     — fraction of cells that are empty

    Added in R63 Train I (ODS format track advancement).
    """
    by_type: dict[str, int] = {}
    total = 0
    for sheet in ods_doc.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                total += 1
                val = cell.get("value")
                text = cell.get("text") or ""
                if val is None and not text.strip():
                    label = "empty"
                elif isinstance(val, (int, float)):
                    label = "numeric"
                elif text.strip():
                    label = "text"
                else:
                    label = "other"
                by_type[label] = by_type.get(label, 0) + 1
    empty_count = by_type.get("empty", 0)
    return {
        "by_type": by_type,
        "total_cells": total,
        "empty_fraction": round(empty_count / total, 4) if total > 0 else 0.0,
    }
