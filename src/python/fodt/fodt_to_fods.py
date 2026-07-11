"""
fodt_to_fods.py — Dogfood export: FODT → FODS using Format Factory libraries.

Reads a Flat ODF Text (.fodt) file using Format Factory's FODT parser
and writes each document block as a FODS row using Format Factory's FODS writer.

Each FODT block becomes one FODS row with columns: block_type, text.

Sprint: FODT-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.parser import parse_fodt  # FF source reader
from fods.writer import write_fods  # FF target writer


def fodt_to_fods(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    skip_empty: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a FODT file to a FODS flat spreadsheet, one row per block.

    Each FODT block (paragraph, heading, list item) becomes one FODS row
    with columns block_type and text.

    Args:
        fodt_path: Path to the source .fodt file.
        dest_path: Path for the output .fods file (parent dirs created).
        include_header: When True, writes a header row (block_type, text).
        skip_empty: When True, blocks with empty text are omitted.
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    def _make_row(values: list[str]) -> dict:
        return {
            "cells": [
                {"value": v, "value_type": "string", "text_content": v}
                for v in values
            ]
        }

    fods_rows: list[dict] = []
    if include_header:
        fods_rows.append(_make_row(["block_type", "text"]))

    data_count = 0
    for block in blocks:
        text = block.get("text", "")
        if skip_empty and not text.strip():
            continue
        block_type = block.get("type", "paragraph")
        fods_rows.append(_make_row([block_type, text]))
        data_count += 1

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return data_count


__all__ = ["fodt_to_fods"]
