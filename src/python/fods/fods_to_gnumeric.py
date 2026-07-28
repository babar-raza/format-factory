"""
fods_to_gnumeric.py — Dogfood export: FODS → Gnumeric using Format Factory libraries.

Sprint: FODS-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fods.parser import parse_fods_strict  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def fods_to_gnumeric(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert FODS to a Gnumeric spreadsheet."""
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)  # Format Factory fods reader
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []

    cell_grid: dict = {}
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for r, row in enumerate(sheet.get("rows", [])):
            for c, cell in enumerate(row.get("cells", [])):
                val = str(cell.get("value", "")) if cell.get("value") is not None else ""
                cell_grid[(r, c)] = val

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(set(r for r, c in cell_grid)) if cell_grid else 0


__all__ = ["fods_to_gnumeric"]
