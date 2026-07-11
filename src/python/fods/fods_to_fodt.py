"""
fods_to_fodt.py — Dogfood export: FODS → FODT using Format Factory libraries.

Reads a FODS file using Format Factory's FODS parser and writes each row
as a FODT paragraph using Format Factory's FODT writer.

Each FODS row becomes one FODT paragraph with cell values joined by ' | '.

Sprint: FODS-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-FODT-DOGFOOD-001

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
from fodt.writer import write_fodt  # FF target writer


def fods_to_fodt(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
    separator: str = " | ",
) -> int:
    """Convert a FODS flat spreadsheet to a FODT flat text document, one paragraph per row.

    Each FODS row becomes one FODT paragraph. Cell values are joined with the separator.

    Args:
        fods_path: Path to the source .fods file.
        dest_path: Path for the output .fodt file (parent dirs created).
        sheet_index: Which sheet to export (0-based, default 0).
        separator: String used to join cell values within a row.

    Returns:
        Number of paragraphs (rows) written.
    """
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)  # Format Factory fods reader
    sheets = doc.get("sheets", [])

    blocks: list[dict] = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for row in sheet.get("rows", []):
            cells = row.get("cells", [])
            cell_texts: list[str] = []
            for cell in cells:
                if cell.get("is_covered"):
                    cell_texts.append("")
                else:
                    value = cell.get("value")
                    cell_texts.append("" if value is None else str(value))
            blocks.append({"type": "paragraph", "text": separator.join(cell_texts)})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["fods_to_fodt"]
