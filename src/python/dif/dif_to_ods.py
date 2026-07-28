"""
dif_to_ods.py — Dogfood export: DIF → ODS using Format Factory libraries.

Reads a DIF file using Format Factory's DIF parser and writes it as an ODS
spreadsheet using Format Factory's ODS writer.

Each DIF row becomes one ODS row.

Sprint: DIF-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from dif.dif_parser import parse_dif_strict  # FF source reader
from ods.ods_parser import OdsCell, OdsDocument, OdsRow, OdsSheet  # FF ODS model
from ods.ods_writer import write_ods  # FF target writer


def dif_to_ods(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
    include_row_index: bool = False,
) -> int:
    """Convert a DIF file to an ODS spreadsheet.

    Each DIF row becomes one ODS row. DIF has no native headers.

    Args:
        dif_path: Path to the source .dif file.
        dest_path: Path for the output .ods file (parent dirs created).
        sheet_name: Name of the output sheet (default "Sheet1").
        include_row_index: When True, prepends a 0-based row index column.

    Returns:
        Number of data rows written.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    ods_rows: list[OdsRow] = []
    for idx, row in enumerate(doc.rows):
        cells: list[OdsCell] = []
        if include_row_index:
            cells.append(OdsCell(text=str(idx)))
        for cell in row:
            raw = str(cell.value) if cell.value is not None else ""
            # DIF string values are quoted (e.g. '"Name"') — strip surrounding quotes
            val = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
            cells.append(OdsCell(text=val))
        ods_rows.append(OdsRow(cells=cells))

    sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    document = OdsDocument(sheets=[sheet])
    write_ods(document, dest_path)  # Format Factory ods writer
    return len(ods_rows)


__all__ = ["dif_to_ods"]
