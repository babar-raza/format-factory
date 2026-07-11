"""
abw_to_fods.py — Dogfood export: ABW → FODS using Format Factory libraries.

Reads an AbiWord (.abw) file using Format Factory's ABW codec and writes each
paragraph as a row in a Flat ODS (.fods) spreadsheet using Format Factory's
FODS writer.

Each ABW paragraph becomes one FODS row with a single 'text' cell.

Sprint: ABW-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "abw"))
sys.path.insert(0, str(_REPO))

from abw.abw_codec import load  # FF source reader
from fods.writer import write_fods  # FF target writer


def abw_to_fods(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    skip_empty: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert an ABW file to a FODS spreadsheet, one row per paragraph.

    Args:
        abw_path: Path to the source .abw file.
        dest_path: Path for the output .fods file (parent dirs created).
        include_header: When True, writes a 'text' header row.
        skip_empty: When True, empty paragraphs are omitted.
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load(abw_path)  # Format Factory abw reader
    raw_paragraphs = model.get("paragraphs", []) or []

    def _make_row(text: str) -> dict:
        return {"cells": [{"value": text, "value_type": "string", "text_content": text}]}

    fods_rows: list[dict] = []
    if include_header:
        fods_rows.append(_make_row("text"))

    data_count = 0
    for para in raw_paragraphs:
        text = para.get("text", "") if isinstance(para, dict) else str(para)
        if skip_empty and not text:
            continue
        fods_rows.append(_make_row(text))
        data_count += 1

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return data_count


__all__ = ["abw_to_fods"]
