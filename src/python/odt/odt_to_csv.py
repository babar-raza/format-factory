"""
odt_to_csv.py — Dogfood export: ODT → CSV using Format Factory libraries.

Reads an OpenDocument Text (.odt) file using Format Factory's ODT parser and
writes each document element (paragraph, heading, list item) as a CSV row
using Format Factory's CSV writer.

Each element becomes one row with columns: element_type, text.

Sprint: ODT-TO-CSV-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-CSV-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import OdtHeading, OdtListItem, OdtParagraph, parse_odt_strict  # FF source reader
from ff_csv.csv_writer import write_csv_to_file  # FF target writer


def odt_to_csv(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    skip_empty: bool = True,
) -> int:
    """Convert an ODT file to CSV, one row per document element.

    Each paragraph, heading, or list item becomes one CSV row with
    columns element_type and text.

    Args:
        odt_path: Path to the source .odt file.
        dest_path: Path for the output .csv file (parent dirs created).
        include_header: When True, writes a header row (element_type,text).
        skip_empty: When True, elements with empty text are omitted.

    Returns:
        Number of data rows written (not counting the header).
    """
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader
    elements = doc.elements

    rows: list[list[str]] = []
    for elem in elements:
        if isinstance(elem, OdtHeading):
            text = elem.text
            etype = "heading"
        elif isinstance(elem, OdtListItem):
            text = elem.text
            etype = "list_item"
        else:
            text = elem.text
            etype = "paragraph"

        if skip_empty and not text:
            continue
        rows.append([etype, text])

    write_csv_to_file(  # Format Factory csv writer
        rows,
        dest_path,
        headers=["element_type", "text"] if include_header else None,
    )
    return len(rows)


__all__ = ["odt_to_csv"]
