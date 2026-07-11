"""
fodg_to_fods.py — Dogfood export: FODG → FODS using Format Factory libraries.

Reads a Flat OpenDocument Drawing (.fodg) file using Format Factory's FODG
codec and writes each drawing page as a FODS row using Format Factory's FODS writer.

Each drawing page becomes one FODS row with columns: page_name, text_content,
shape_count.

Sprint: FODG-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodg"))
sys.path.insert(0, str(_REPO))

from fodg.fodg_codec import load as load_fodg  # FF source reader
from fods.writer import write_fods  # FF target writer


def fodg_to_fods(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a FODG drawing file to a FODS flat spreadsheet, one row per page.

    Each drawing page becomes one FODS row with columns page_name, text_content,
    and shape_count. Multiple text content items are joined with '; '.

    Args:
        fodg_path: Path to the source .fodg file.
        dest_path: Path for the output .fods file (parent dirs created).
        include_header: When True, writes a header row.
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    def _make_row(values: list[str]) -> dict:
        return {
            "cells": [
                {"value": v, "value_type": "string", "text_content": v}
                for v in values
            ]
        }

    fods_rows: list[dict] = []
    if include_header:
        fods_rows.append(_make_row(["page_name", "text_content", "shape_count"]))

    for page in pages:
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)
        shape_count = str(page.get("shape_count", 0))
        fods_rows.append(_make_row([page_name, text_content, shape_count]))

    data_count = len(pages)
    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return data_count


__all__ = ["fodg_to_fods"]
