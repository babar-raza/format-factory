"""
sylk_to_fods.py — Dogfood export: SYLK → FODS using Format Factory libraries.

Reads a SYLK file using Format Factory's SYLK parser and writes it as a
Flat ODS (.fods) spreadsheet using Format Factory's FODS writer.

Each SYLK row becomes one FODS row.

Sprint: SYLK-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from fods.writer import write_fods  # FF target writer


def sylk_to_fods(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a SYLK file to a FODS flat spreadsheet.

    SYLK uses 1-based (row, col) coordinates. Cells are collected into a grid
    and written row by row into FODS format.

    Args:
        sylk_path: Path to the source .slk file.
        dest_path: Path for the output .fods file (parent dirs created).
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of rows written.
    """
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    # Build a grid: {row: {col: value_str}}
    grid: dict[int, dict[int, str]] = {}
    for cell in doc.cells:
        r, c = cell.row, cell.col
        grid.setdefault(r, {})[c] = str(cell.value) if cell.value is not None else ""

    def _make_row(values: list[str]) -> dict:
        return {
            "cells": [
                {"value": v, "value_type": "string", "text_content": v}
                for v in values
            ]
        }

    if not grid:
        workbook = {"sheets": [{"name": sheet_name, "rows": []}]}
        write_fods(workbook, dest_path)
        return 0

    max_row = max(grid)
    max_col = max(c for row_cells in grid.values() for c in row_cells)

    fods_rows: list[dict] = []
    for r in range(1, max_row + 1):
        row_cells = grid.get(r, {})
        row_vals = [row_cells.get(c, "") for c in range(1, max_col + 1)]
        fods_rows.append(_make_row(row_vals))

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return len(fods_rows)


__all__ = ["sylk_to_fods"]
