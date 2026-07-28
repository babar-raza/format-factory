"""
ods_to_fods.py — Dogfood export: ODS → FODS using Format Factory libraries.

Reads an ODS (.ods) spreadsheet using Format Factory's ODS parser and writes
it as a Flat ODS (.fods) file using Format Factory's FODS writer.

Each ODS sheet becomes a FODS sheet; cell text/values are preserved.

Sprint: ODS-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # FF source reader
from fods.writer import write_fods  # FF target writer


def ods_to_fods(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int | None = None,
    skip_empty_rows: bool = False,
) -> int:
    """Convert an ODS spreadsheet to FODS format.

    Args:
        ods_path: Path to the source .ods file.
        dest_path: Path for the output .fods file (parent dirs created).
        sheet_index: If given, export only that sheet (0-based); otherwise all sheets.
        skip_empty_rows: When True, rows where all cells are empty are omitted.

    Returns:
        Total number of rows written across all exported sheets.
    """
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader

    sheets_to_export = doc.sheets
    if sheet_index is not None:
        sheets_to_export = [doc.sheets[sheet_index]]

    fods_sheets: list[dict] = []
    total_rows = 0

    for sheet in sheets_to_export:
        fods_rows: list[dict] = []
        for row in sheet.rows:
            cells: list[dict] = []
            for cell in row.cells:
                text = cell.text if cell.text else (str(cell.value) if cell.value is not None else "")
                cells.append({"value": text, "value_type": "string", "text_content": text})
            if skip_empty_rows and all(c["value"] == "" for c in cells):
                continue
            fods_rows.append({"cells": cells})
            total_rows += 1
        fods_sheets.append({"name": sheet.name, "rows": fods_rows})

    workbook = {"sheets": fods_sheets}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return total_rows


__all__ = ["ods_to_fods"]
