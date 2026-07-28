"""
fods_to_dif.py — Dogfood export: FODS → DIF using Format Factory libraries.

Sprint: FODS-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fods.parser import parse_fods_strict  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def fods_to_dif(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    title: str = "FODS Export",
) -> int:
    """Convert a FODS flat spreadsheet to a DIF file."""
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)  # Format Factory fods reader
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []

    dif_rows = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for row in sheet.get("rows", []):
            cells = []
            for cell in row.get("cells", []):
                val = str(cell.get("value", "")) if cell.get("value") is not None else ""
                cells.append(DifCell(value=val, value_type="string"))
            dif_rows.append(cells)

    dif_doc = DifDocument(title=title, rows=dif_rows)
    write_dif(dif_doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["fods_to_dif"]
