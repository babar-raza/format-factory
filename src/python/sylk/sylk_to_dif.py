"""
sylk_to_dif.py — Dogfood export: SYLK → DIF using Format Factory libraries.

Sprint: SYLK-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-SYLK-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from sylk.sylk_parser import parse_sylk_strict  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def sylk_to_dif(
    sylk_path: str | Path,
    dest_path: str | Path,
    *,
    title: str = "SYLK Export",
) -> int:
    """Convert a SYLK file to a DIF file."""
    sylk_path = Path(sylk_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_sylk_strict(sylk_path)  # Format Factory sylk reader

    # Rebuild row-major grid (1-based)
    grid: dict[int, dict[int, str]] = {}
    for cell in doc.cells:
        r, c = cell.row, cell.col
        grid.setdefault(r, {})[c] = str(cell.value) if cell.value is not None else ""

    dif_rows = []
    if grid:
        max_row = max(grid)
        max_col = max(c for row_cells in grid.values() for c in row_cells)
        for row_idx in range(1, max_row + 1):
            row_cells = grid.get(row_idx, {})
            cells = [DifCell(value=row_cells.get(col_idx, ""), value_type="string") for col_idx in range(1, max_col + 1)]
            dif_rows.append(cells)

    dif_doc = DifDocument(title=title, rows=dif_rows)
    write_dif(dif_doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["sylk_to_dif"]
