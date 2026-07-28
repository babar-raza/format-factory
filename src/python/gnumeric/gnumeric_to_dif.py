"""
gnumeric_to_dif.py — Dogfood export: Gnumeric → DIF using Format Factory libraries.

Sprint: GNUMERIC-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path


from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def gnumeric_to_dif(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    title: str = "Gnumeric Export",
) -> int:
    """Convert a Gnumeric file to a DIF file."""
    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader
    sheets = model.get("sheets", [])

    dif_rows = []
    if sheets and sheet_index < len(sheets):
        cell_grid: dict = sheets[sheet_index].get("cell_grid", {})
        if cell_grid:
            max_row = max(r for r, c in cell_grid)
            max_col = max(c for r, c in cell_grid)
            for row_idx in range(max_row + 1):
                cells = []
                for col_idx in range(max_col + 1):
                    val = str(cell_grid.get((row_idx, col_idx), ""))
                    cells.append(DifCell(value=val, value_type="string"))
                dif_rows.append(cells)

    doc = DifDocument(title=title, rows=dif_rows)
    write_dif(doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["gnumeric_to_dif"]
