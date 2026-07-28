"""
ods_to_abw.py — Dogfood export: ODS → ABW using Format Factory libraries.

Reads an ODS file using Format Factory's ODS parser and writes each row
as an ABW paragraph using Format Factory's ABW writer.

Each ODS row becomes one ABW paragraph with cell values joined by ' | '.

Sprint: ODS-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from ods.ods_parser import parse_ods_strict  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def ods_to_abw(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    separator: str = " | ",
) -> int:
    """Convert an ODS spreadsheet to an ABW document, one paragraph per row.

    Each ODS row becomes one ABW paragraph. Cell values are joined with
    the separator string.

    Args:
        ods_path: Path to the source .ods file.
        dest_path: Path for the output .abw file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        separator: String used to join cell values within a row.

    Returns:
        Number of paragraphs (rows) written.
    """
    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader
    sheets = doc.sheets if hasattr(doc, "sheets") else []

    paragraphs: list[str] = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for row in sheet.rows:
            parts: list[str] = []
            for cell in row.cells:
                text = cell.text if cell.text else (str(cell.value) if cell.value is not None else "")
                parts.append(text)
            paragraphs.append(separator.join(parts))

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["ods_to_abw"]
