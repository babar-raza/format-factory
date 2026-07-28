"""
fodp_to_fods.py — Dogfood export: FODP → FODS using Format Factory libraries.

Reads a Flat OpenDocument Presentation (.fodp) file using Format Factory's
FODP codec and writes each slide as a FODS row using Format Factory's FODS writer.

Each slide becomes one FODS row with columns: slide_name, title, text_content.

Sprint: FODP-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodp.fodp_codec import load as load_fodp  # FF source reader
from fods.writer import write_fods  # FF target writer


def fodp_to_fods(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a FODP presentation to a FODS flat spreadsheet, one row per slide.

    Each slide becomes one FODS row with columns slide_name, title, text_content.
    Multiple text content items are joined with '; '.

    Args:
        fodp_path: Path to the source .fodp file.
        dest_path: Path for the output .fods file (parent dirs created).
        include_header: When True, writes a header row.
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
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
        fods_rows.append(_make_row(["slide_name", "title", "text_content"]))

    for page in pages:
        slide_name = page.get("name", "") or ""
        title = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)
        fods_rows.append(_make_row([slide_name, title, text_content]))

    data_count = len(pages)
    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return data_count


__all__ = ["fodp_to_fods"]
