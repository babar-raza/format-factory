"""
dif_to_gnumeric.py — Dogfood export: DIF → Gnumeric using Format Factory libraries.

Sprint: DIF-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from dif.dif_parser import parse_dif_strict  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def dif_to_gnumeric(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert DIF to a Gnumeric spreadsheet."""
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    cell_grid: dict = {}
    for r, row in enumerate(doc.rows):
        for c, cell in enumerate(row):
            raw = str(cell.value) if cell.value is not None else ""
            val = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
            cell_grid[(r, c)] = val

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(doc.rows)


__all__ = ["dif_to_gnumeric"]
