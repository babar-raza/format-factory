"""
ods_to_dif.py — Dogfood export: ODS → DIF using Format Factory libraries.

Sprint: ODS-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def ods_to_dif(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    title: str = "ODS Export",
) -> int:
    """Convert an ODS spreadsheet to a DIF file."""
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader
    sheets = doc.sheets if hasattr(doc, "sheets") else []

    dif_rows = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for row in sheet.rows:
            cells = []
            for cell in row.cells:
                text = cell.text if cell.text else (str(cell.value) if cell.value is not None else "")
                cells.append(DifCell(value=text, value_type="string"))
            dif_rows.append(cells)

    dif_doc = DifDocument(title=title, rows=dif_rows)
    write_dif(dif_doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["ods_to_dif"]
