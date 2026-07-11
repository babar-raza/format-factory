"""
fods_to_ods.py — Dogfood export: FODS → ODS using Format Factory libraries.

Reads a Flat ODS (.fods) file using Format Factory's FODS parser and writes
one sheet's rows to an ODS file using Format Factory's ODS writer.

Each FODS row becomes an ODS row; cell values are converted to strings.
Covered cells (span overflows) are emitted as empty strings.

Sprint: FODS-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fods.parser import parse_fods_strict  # FF source reader
from ods.ods_writer import write_ods  # FF target writer
from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell  # FF ODS model


def fods_to_ods(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    sheet_name: str = "Sheet1",
    skip_empty_rows: bool = True,
) -> int:
    """Convert one sheet of a FODS file to ODS format.

    Args:
        fods_path: Path to the source .fods file.
        dest_path: Path for the output .ods file (parent dirs created).
        sheet_index: Zero-based index of the sheet to export (default 0).
        sheet_name: Name for the ODS sheet tab.
        skip_empty_rows: When True, rows where all cells are empty are omitted.

    Returns:
        Number of ODS rows written.
    """
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)  # Format Factory fods reader
    sheets = doc.get("sheets", [])

    if not sheets:
        ods_doc = OdsDocument(sheets=[OdsSheet(name=sheet_name, rows=[])])
        write_ods(ods_doc, dest_path)  # Format Factory ods writer
        return 0

    sheet = sheets[sheet_index]
    rows_data = sheet.get("rows", [])

    ods_rows: list[OdsRow] = []
    for row in rows_data:
        cells = row.get("cells", [])
        ods_cells: list[OdsCell] = []
        for cell in cells:
            if cell.get("is_covered"):
                ods_cells.append(OdsCell(text=""))
            else:
                value = cell.get("value")
                ods_cells.append(OdsCell(text="" if value is None else str(value)))
        if skip_empty_rows and all(c.text == "" for c in ods_cells):
            continue
        ods_rows.append(OdsRow(cells=ods_cells))

    ods_sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    ods_doc = OdsDocument(sheets=[ods_sheet])
    write_ods(ods_doc, dest_path)  # Format Factory ods writer
    return len(ods_rows)


__all__ = ["fods_to_ods"]
