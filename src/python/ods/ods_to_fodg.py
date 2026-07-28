"""
ods_to_fodg.py — Dogfood export: ODS → FODG using Format Factory libraries.

Sprint: ODS-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def ods_to_fodg(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert an ODS spreadsheet to a FODG drawing, one page per row."""
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader
    sheets = doc.sheets if hasattr(doc, "sheets") else []

    pages_list = []
    if sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        rows = sheet.rows if hasattr(sheet, "rows") else []
        for i, row in enumerate(rows):
            row_cells = row.cells if hasattr(row, "cells") else []
            texts = [str(c.value) for c in row_cells if c.value is not None]
            pages_list.append({"name": f"Row{i + 1}", "texts": texts})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["ods_to_fodg"]
