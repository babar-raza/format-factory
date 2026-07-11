"""
gnumeric_to_ods.py — Dogfood export: Gnumeric → ODS using Format Factory libraries.

Reads a Gnumeric (.gnumeric) file using Format Factory's Gnumeric codec and writes
the selected sheet's rows to an ODS spreadsheet using Format Factory's ODS writer.

Each row in the sheet's cell_grid becomes one ODS row.

Sprint: GNUMERIC-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "gnumeric"))
sys.path.insert(0, str(_REPO))

from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from ods.ods_writer import write_ods  # FF target writer
from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell  # FF ODS model


def gnumeric_to_ods(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    sheet_name: str = "Sheet1",
    include_row_index: bool = False,
) -> int:
    """Convert a Gnumeric spreadsheet to ODS format.

    Args:
        gnumeric_path: Path to the source .gnumeric file.
        dest_path: Path for the output .ods file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        sheet_name: Name for the ODS sheet tab.
        include_row_index: When True, prepend a 0-based row number column.

    Returns:
        Number of ODS rows written.
    """
    from gnumeric.exceptions import GnumericError

    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader

    sheets: list = model.get("sheets", [])
    if not sheets:
        doc = OdsDocument(sheets=[OdsSheet(name=sheet_name, rows=[])])
        write_ods(doc, dest_path)  # Format Factory ods writer
        return 0

    if sheet_index < 0 or sheet_index >= len(sheets):
        raise GnumericError(
            f"sheet_index {sheet_index} out of range (0..{len(sheets) - 1})"
        )

    sheet = sheets[sheet_index]
    cell_grid: dict = sheet.get("cell_grid", {})

    if not cell_grid:
        doc = OdsDocument(sheets=[OdsSheet(name=sheet_name, rows=[])])
        write_ods(doc, dest_path)  # Format Factory ods writer
        return 0

    max_row = max(r for r, c in cell_grid)
    max_col = max(c for r, c in cell_grid)

    ods_rows: list[OdsRow] = []
    for row_idx in range(max_row + 1):
        cells: list[OdsCell] = []
        if include_row_index:
            cells.append(OdsCell(text=str(row_idx)))
        for col_idx in range(max_col + 1):
            cells.append(OdsCell(text=str(cell_grid.get((row_idx, col_idx), ""))))
        ods_rows.append(OdsRow(cells=cells))

    ods_sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    doc = OdsDocument(sheets=[ods_sheet])
    write_ods(doc, dest_path)  # Format Factory ods writer
    return len(ods_rows)


__all__ = ["gnumeric_to_ods"]
