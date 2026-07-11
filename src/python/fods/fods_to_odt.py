"""
fods_to_odt.py — Dogfood export: FODS → ODT using Format Factory libraries.

Reads a Flat ODS (.fods) file using Format Factory's FODS parser and writes
each row as an ODT paragraph using Format Factory's ODT writer.

Each FODS row becomes one ODT paragraph, with cell values joined by a
configurable separator.

Sprint: FODS-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "src" / "python" / "fods"))
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fods.parser import parse_fods_strict  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def fods_to_odt(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    separator: str = "\t",
    skip_empty_rows: bool = True,
) -> int:
    """Convert one sheet of a FODS file to an ODT document.

    Args:
        fods_path: Path to the source .fods file.
        dest_path: Path for the output .odt file (parent dirs created).
        sheet_index: Zero-based index of the sheet to export (default 0).
        separator: String used to join cell values within each paragraph.
        skip_empty_rows: When True, rows where all cells are empty are omitted.

    Returns:
        Number of paragraphs written.
    """
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)  # Format Factory fods reader
    sheets = doc.get("sheets", [])

    if not sheets:
        write_odt([], dest_path)  # Format Factory odt writer
        return 0

    sheet = sheets[sheet_index]
    rows_data = sheet.get("rows", [])

    paragraphs: list[str] = []
    for row in rows_data:
        cells = row.get("cells", [])
        parts: list[str] = []
        for cell in cells:
            if cell.get("is_covered"):
                parts.append("")
            else:
                value = cell.get("value")
                parts.append("" if value is None else str(value))
        if skip_empty_rows and all(p == "" for p in parts):
            continue
        paragraphs.append(separator.join(parts))

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["fods_to_odt"]
