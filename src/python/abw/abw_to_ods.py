"""
abw_to_ods.py — Dogfood export: ABW → ODS using Format Factory libraries.

Reads an AbiWord (.abw) file using Format Factory's ABW codec and writes each
paragraph as an ODS row using Format Factory's ODS writer.

Each ABW paragraph becomes one ODS row with a single 'text' column.

Sprint: ABW-TO-ODS-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-ODS-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "abw"))

from abw.abw_codec import load  # FF source reader
from ods.ods_parser import OdsCell, OdsDocument, OdsRow, OdsSheet  # FF ODS model
from ods.ods_writer import write_ods  # FF target writer


def abw_to_ods(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    include_header: bool = True,
    skip_empty: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert an ABW file to an ODS spreadsheet, one row per paragraph.

    Each ABW paragraph becomes one ODS row with a single 'text' column.

    Args:
        abw_path: Path to the source .abw file.
        dest_path: Path for the output .ods file (parent dirs created).
        include_header: When True, writes a header row with 'text' column name.
        skip_empty: When True, empty paragraphs are omitted.
        sheet_name: Name of the output sheet (default "Sheet1").

    Returns:
        Number of data rows written (not counting the header).
    """
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load(abw_path)  # Format Factory abw reader
    raw_paragraphs = model.get("paragraphs", []) or []

    ods_rows: list[OdsRow] = []
    if include_header:
        ods_rows.append(OdsRow(cells=[OdsCell(text="text")]))

    data_rows: list[str] = []
    for para in raw_paragraphs:
        text = para.get("text", "") if isinstance(para, dict) else str(para)
        if skip_empty and not text:
            continue
        data_rows.append(text)
        ods_rows.append(OdsRow(cells=[OdsCell(text=text)]))

    sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    doc = OdsDocument(sheets=[sheet])
    write_ods(doc, dest_path)  # Format Factory ods writer
    return len(data_rows)


__all__ = ["abw_to_ods"]
