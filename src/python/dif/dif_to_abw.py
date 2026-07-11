"""
dif_to_abw.py — Dogfood export: DIF → ABW using Format Factory libraries.

Reads a DIF file using Format Factory's DIF parser and writes each row
as an ABW paragraph using Format Factory's ABW writer.

Each DIF row becomes one ABW paragraph with cell values joined by ' | '.

Sprint: DIF-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "dif"))

from dif.dif_parser import parse_dif_strict  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def dif_to_abw(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " | ",
) -> int:
    """Convert a DIF file to an ABW document, one paragraph per row.

    Each DIF row becomes one ABW paragraph. DIF string values have surrounding
    quotes stripped. Cell values are joined with the separator string.

    Args:
        dif_path: Path to the source .dif file.
        dest_path: Path for the output .abw file (parent dirs created).
        separator: String used to join cell values within a row.

    Returns:
        Number of paragraphs (rows) written.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    paragraphs: list[str] = []
    for row in doc.rows:
        row_vals: list[str] = []
        for cell in row:
            raw = str(cell.value) if cell.value is not None else ""
            val = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
            row_vals.append(val)
        paragraphs.append(separator.join(row_vals))

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["dif_to_abw"]
