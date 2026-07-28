"""
dif_to_fodt.py — Dogfood export: DIF → FODT using Format Factory libraries.

Reads a DIF file using Format Factory's DIF parser and writes each row
as a FODT paragraph using Format Factory's FODT writer.

Each DIF row becomes one FODT paragraph with cell values joined by ' | '.

Sprint: DIF-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from dif.dif_parser import parse_dif_strict  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def dif_to_fodt(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " | ",
) -> int:
    """Convert a DIF file to a FODT flat text document, one paragraph per row.

    Each DIF row becomes one FODT paragraph. DIF string values have surrounding
    quotes stripped. Cell values are joined with the separator string.

    Args:
        dif_path: Path to the source .dif file.
        dest_path: Path for the output .fodt file (parent dirs created).
        separator: String used to join cell values within a row.

    Returns:
        Number of paragraphs (rows) written.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    blocks: list[dict] = []
    for row in doc.rows:
        row_vals: list[str] = []
        for cell in row:
            raw = str(cell.value) if cell.value is not None else ""
            val = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
            row_vals.append(val)
        blocks.append({"type": "paragraph", "text": separator.join(row_vals)})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["dif_to_fodt"]
