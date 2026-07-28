"""
sylk_to_gnumeric.py — Dogfood export: SYLK → Gnumeric using Format Factory libraries.

Sprint: SYLK-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def sylk_to_gnumeric(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert SYLK to a Gnumeric spreadsheet."""
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    cell_grid: dict = {}
    for cell in doc.cells:
        r, c = cell.row - 1, cell.col - 1  # convert 1-based to 0-based
        cell_grid[(r, c)] = str(cell.value) if cell.value is not None else ""

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(set(r for r, c in cell_grid)) if cell_grid else 0


__all__ = ["sylk_to_gnumeric"]
