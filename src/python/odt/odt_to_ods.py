"""
odt_to_ods.py — Dogfood export: ODT → ODS using Format Factory libraries.

Reads an OpenDocument Text (.odt) file using Format Factory's ODT parser
and writes each document element as an ODS row using Format Factory's ODS writer.

Each element (paragraph, heading, list item) becomes one ODS row with
columns: element_type, text.

Sprint: ODT-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import OdtHeading, OdtListItem, parse_odt_strict  # FF source reader
from ods.ods_writer import write_ods  # FF target writer
from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell  # FF ODS model


def odt_to_ods(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    skip_empty: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert an ODT file to ODS, one row per document element.

    Each paragraph, heading, or list item becomes one ODS row with
    columns element_type and text.

    Args:
        odt_path: Path to the source .odt file.
        dest_path: Path for the output .ods file (parent dirs created).
        include_header: When True, writes a header row (element_type, text).
        skip_empty: When True, elements with empty text are omitted.
        sheet_name: Name for the ODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader
    elements = doc.elements

    ods_rows: list[OdsRow] = []
    if include_header:
        ods_rows.append(OdsRow(cells=[OdsCell(text="element_type"), OdsCell(text="text")]))

    data_count = 0
    for elem in elements:
        if isinstance(elem, OdtHeading):
            etype, text = "heading", elem.text
        elif isinstance(elem, OdtListItem):
            etype, text = "list_item", elem.text
        else:
            etype, text = "paragraph", elem.text

        if skip_empty and not text:
            continue
        ods_rows.append(OdsRow(cells=[OdsCell(text=etype), OdsCell(text=text)]))
        data_count += 1

    ods_sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    ods_doc = OdsDocument(sheets=[ods_sheet])
    write_ods(ods_doc, dest_path)  # Format Factory ods writer
    return data_count


__all__ = ["odt_to_ods"]
