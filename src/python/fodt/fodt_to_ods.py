"""
fodt_to_ods.py — Dogfood export: FODT → ODS using Format Factory libraries.

Reads a Flat OpenDocument Text (.fodt) file using Format Factory's FODT parser
and writes each document block as an ODS row using Format Factory's ODS writer.

Each block (paragraph or heading) becomes one ODS row with columns:
block_type and text.

Sprint: FODT-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodt"))
sys.path.insert(0, str(_REPO))

from fodt.parser import parse_fodt  # FF source reader
from ods.ods_writer import write_ods  # FF target writer
from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell  # FF ODS model


def fodt_to_ods(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    skip_empty: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert a FODT file to ODS, one row per document block.

    Args:
        fodt_path: Path to the source .fodt file.
        dest_path: Path for the output .ods file (parent dirs created).
        include_header: When True, writes a header row (block_type, text).
        skip_empty: When True, blocks with empty text are omitted.
        sheet_name: Name for the ODS sheet tab.

    Returns:
        Number of data rows written (not counting the header).
    """
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    ods_rows: list[OdsRow] = []
    if include_header:
        ods_rows.append(OdsRow(cells=[OdsCell(text="block_type"), OdsCell(text="text")]))

    data_count = 0
    for block in blocks:
        block_type = block.get("type", "paragraph")
        text = block.get("text", "")
        if skip_empty and not text:
            continue
        ods_rows.append(OdsRow(cells=[OdsCell(text=block_type), OdsCell(text=text)]))
        data_count += 1

    ods_sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    ods_doc = OdsDocument(sheets=[ods_sheet])
    write_ods(ods_doc, dest_path)  # Format Factory ods writer
    return data_count


__all__ = ["fodt_to_ods"]
