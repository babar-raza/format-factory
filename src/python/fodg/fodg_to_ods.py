"""
fodg_to_ods.py — Dogfood export: FODG → ODS using Format Factory libraries.

Reads a Flat OpenDocument Drawing (.fodg) file using Format Factory's FODG
codec and writes each page as an ODS row using Format Factory's ODS writer.

Each drawing page becomes one ODS row with columns: page_name, text_content,
and optionally shape_count and page_index.

Sprint: FODG-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodg.fodg_codec import load as load_fodg  # FF source reader
from ods.ods_writer import write_ods  # FF target writer
from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell  # FF ODS model


def fodg_to_ods(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    include_page_index: bool = False,
    include_shape_count: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a FODG drawing file to ODS, one row per page.

    Args:
        fodg_path: Path to the source .fodg file.
        dest_path: Path for the output .ods file (parent dirs created).
        include_header: When True, writes a header row.
        include_page_index: When True, adds a page_index column (0-based).
        include_shape_count: When True, adds a shape_count column.
        sheet_name: Name for the ODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    col_headers: list[str] = []
    if include_page_index:
        col_headers.append("page_index")
    col_headers.append("page_name")
    col_headers.append("text_content")
    if include_shape_count:
        col_headers.append("shape_count")

    ods_rows: list[OdsRow] = []
    if include_header:
        ods_rows.append(OdsRow(cells=[OdsCell(text=h) for h in col_headers]))

    for idx, page in enumerate(pages):
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)
        shape_count = str(page.get("shape_count", 0))

        cells: list[OdsCell] = []
        if include_page_index:
            cells.append(OdsCell(text=str(idx)))
        cells.append(OdsCell(text=page_name))
        cells.append(OdsCell(text=text_content))
        if include_shape_count:
            cells.append(OdsCell(text=shape_count))
        ods_rows.append(OdsRow(cells=cells))

    ods_sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    ods_doc = OdsDocument(sheets=[ods_sheet])
    write_ods(ods_doc, dest_path)  # Format Factory ods writer
    return len(pages)


__all__ = ["fodg_to_ods"]
