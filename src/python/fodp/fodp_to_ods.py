"""
fodp_to_ods.py — Dogfood export: FODP → ODS using Format Factory libraries.

Reads a Flat OpenDocument Presentation (.fodp) file using Format Factory's
FODP codec and writes each slide as an ODS row using Format Factory's ODS writer.

Each slide becomes one ODS row with columns: slide_name, title, text_content.

Sprint: FODP-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodp.fodp_codec import load as load_fodp  # FF source reader
from ods.ods_writer import write_ods  # FF target writer
from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell  # FF ODS model


def fodp_to_ods(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    include_slide_index: bool = False,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a FODP presentation to ODS, one row per slide.

    Args:
        fodp_path: Path to the source .fodp file.
        dest_path: Path for the output .ods file (parent dirs created).
        include_header: When True, writes a header row.
        include_slide_index: When True, adds a slide_index column (0-based).
        sheet_name: Name for the ODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    col_headers: list[str] = []
    if include_slide_index:
        col_headers.append("slide_index")
    col_headers.extend(["slide_name", "title", "text_content"])

    ods_rows: list[OdsRow] = []
    if include_header:
        ods_rows.append(OdsRow(cells=[OdsCell(text=h) for h in col_headers]))

    for idx, page in enumerate(pages):
        slide_name = page.get("name", "") or ""
        title = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)

        cells: list[OdsCell] = []
        if include_slide_index:
            cells.append(OdsCell(text=str(idx)))
        cells.extend([
            OdsCell(text=slide_name),
            OdsCell(text=title),
            OdsCell(text=text_content),
        ])
        ods_rows.append(OdsRow(cells=cells))

    ods_sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    ods_doc = OdsDocument(sheets=[ods_sheet])
    write_ods(ods_doc, dest_path)  # Format Factory ods writer
    return len(pages)


__all__ = ["fodp_to_ods"]
