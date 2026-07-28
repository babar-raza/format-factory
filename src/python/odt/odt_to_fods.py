"""
odt_to_fods.py — Dogfood export: ODT → FODS using Format Factory libraries.

Reads an OpenDocument Text (.odt) file using Format Factory's ODT parser
and writes each document element as a FODS row using Format Factory's FODS writer.

Each element (paragraph, heading, list item) becomes one FODS row with
columns: element_type, text.

Sprint: ODT-TO-FODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-FODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import OdtHeading, OdtListItem, parse_odt_strict  # FF source reader
from fods.writer import write_fods  # FF target writer


def odt_to_fods(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    skip_empty: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert an ODT file to a FODS flat spreadsheet, one row per document element.

    Each paragraph, heading, or list item becomes one FODS row with
    columns element_type and text.

    Args:
        odt_path: Path to the source .odt file.
        dest_path: Path for the output .fods file (parent dirs created).
        include_header: When True, writes a header row (element_type, text).
        skip_empty: When True, elements with empty text are omitted.
        sheet_name: Name for the FODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader
    elements = doc.elements

    def _make_row(values: list[str]) -> dict:
        return {
            "cells": [
                {"value": v, "value_type": "string", "text_content": v}
                for v in values
            ]
        }

    fods_rows: list[dict] = []
    if include_header:
        fods_rows.append(_make_row(["element_type", "text"]))

    data_count = 0
    for elem in elements:
        text = elem.text if elem.text else ""
        if skip_empty and not text.strip():
            continue
        if isinstance(elem, OdtHeading):
            elem_type = "heading"
        elif isinstance(elem, OdtListItem):
            elem_type = "list_item"
        else:
            elem_type = "paragraph"
        fods_rows.append(_make_row([elem_type, text]))
        data_count += 1

    workbook = {"sheets": [{"name": sheet_name, "rows": fods_rows}]}
    write_fods(workbook, dest_path)  # Format Factory fods writer
    return data_count


__all__ = ["odt_to_fods"]
