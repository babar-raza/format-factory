"""
gnumeric_to_fods.py — Dogfood export: Gnumeric → FODS using Format Factory libraries.

Reads a Gnumeric file using Format Factory's Gnumeric codec and writes it as a
Flat ODS (.fods) spreadsheet using Format Factory's FODS writer.

Each Gnumeric row becomes one FODS row.

Sprint: GNUMERIC-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from fods.writer import write_fods  # FF target writer


def gnumeric_to_fods(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a Gnumeric file to a FODS flat spreadsheet.

    Each row in the first (or selected) sheet becomes one FODS row. Cells are
    read from the cell_grid and written in row-major order.

    Args:
        gnumeric_path: Path to the source .gnumeric file.
        dest_path: Path for the output .fods file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of rows written.
    """
    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader
    sheets = model.get("sheets", [])

    def _make_row(values: list[str]) -> dict:
        return {
            "cells": [
                {"value": v, "value_type": "string", "text_content": v}
                for v in values
            ]
        }

    if not sheets or sheet_index >= len(sheets):
        workbook = {"sheets": [{"name": sheet_name, "rows": []}]}
        write_fods(workbook, dest_path)
        return 0

    cell_grid: dict = sheets[sheet_index].get("cell_grid", {})

    if not cell_grid:
        workbook = {"sheets": [{"name": sheet_name, "rows": []}]}
        write_fods(workbook, dest_path)
        return 0

    max_row = max(r for r, c in cell_grid)
    max_col = max(c for r, c in cell_grid)

    fods_rows: list[dict] = []
    for row_idx in range(max_row + 1):
        row_vals = [
            str(cell_grid.get((row_idx, col_idx), ""))
            for col_idx in range(max_col + 1)
        ]
        fods_rows.append(_make_row(row_vals))

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return len(fods_rows)


__all__ = ["gnumeric_to_fods"]
