"""
dif_to_fods.py — Dogfood export: DIF → FODS using Format Factory libraries.

Reads a DIF file using Format Factory's DIF parser and writes it as a
Flat ODS (.fods) spreadsheet using Format Factory's FODS writer.

Each DIF row becomes one FODS row.

Sprint: DIF-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "dif"))

from dif.dif_parser import parse_dif_strict  # FF source reader
from fods.writer import write_fods  # FF target writer


def dif_to_fods(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a DIF file to a FODS flat spreadsheet.

    Each DIF row becomes one FODS row. DIF has no native headers.
    DIF string values are stored with surrounding quotes (e.g. '"Name"')
    which are stripped during conversion.

    Args:
        dif_path: Path to the source .dif file.
        dest_path: Path for the output .fods file (parent dirs created).
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of rows written.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    def _make_row(values: list[str]) -> dict:
        return {
            "cells": [
                {"value": v, "value_type": "string", "text_content": v}
                for v in values
            ]
        }

    fods_rows: list[dict] = []
    for row in doc.rows:
        row_vals: list[str] = []
        for cell in row:
            raw = str(cell.value) if cell.value is not None else ""
            # DIF string values are quoted (e.g. '"Name"') — strip surrounding quotes
            val = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
            row_vals.append(val)
        fods_rows.append(_make_row(row_vals))

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return len(fods_rows)


__all__ = ["dif_to_fods"]
