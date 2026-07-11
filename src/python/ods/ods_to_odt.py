"""
ods_to_odt.py — Dogfood export: ODS → ODT using Format Factory libraries.

Reads an ODS (.ods) spreadsheet using Format Factory's ODS parser and writes
each row as an ODT paragraph using Format Factory's ODT writer.

Each ODS row becomes one ODT paragraph, with cell values joined by a
configurable separator.

Sprint: ODS-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODS-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "ods"))
sys.path.insert(0, str(_REPO))

from ods.ods_parser import parse_ods_strict  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def ods_to_odt(
    ods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    separator: str = "\t",
    skip_empty_rows: bool = True,
) -> int:
    """Convert an ODS spreadsheet sheet to an ODT document.

    Args:
        ods_path: Path to the source .ods file.
        dest_path: Path for the output .odt file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        separator: String used to join cell values within each paragraph.
        skip_empty_rows: When True, rows where all cells are empty are omitted.

    Returns:
        Number of paragraphs written.
    """
    from ods.ods_parser import OdsError

    ods_path = Path(ods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_ods_strict(ods_path)  # Format Factory ods reader

    if not doc.sheets:
        write_odt([], dest_path)  # Format Factory odt writer
        return 0

    if sheet_index < 0 or sheet_index >= len(doc.sheets):
        raise OdsError(
            f"sheet_index {sheet_index} out of range (0..{len(doc.sheets) - 1})"
        )

    sheet = doc.sheets[sheet_index]
    paragraphs: list[str] = []
    for row in sheet.rows:
        fields = [
            cell.text if cell.text else (str(cell.value) if cell.value is not None else "")
            for cell in row.cells
        ]
        if skip_empty_rows and all(f == "" for f in fields):
            continue
        paragraphs.append(separator.join(fields))

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["ods_to_odt"]
