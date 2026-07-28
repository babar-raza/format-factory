"""
ods_to_gnumeric.py — Dogfood export: ODS → Gnumeric using Format Factory libraries.

Sprint: ODS-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def ods_to_gnumeric(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert ODS to a Gnumeric spreadsheet."""
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader
    sheets = doc.sheets if hasattr(doc, "sheets") else []

    cell_grid: dict = {}
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for r, row in enumerate(sheet.rows):
            for c, cell in enumerate(row.cells):
                text = cell.text if cell.text else (str(cell.value) if cell.value is not None else "")
                cell_grid[(r, c)] = text

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(set(r for r, c in cell_grid)) if cell_grid else 0


__all__ = ["ods_to_gnumeric"]
