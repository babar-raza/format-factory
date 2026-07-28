"""
dif_to_odt.py — Dogfood export: DIF → ODT using Format Factory libraries.

Reads a DIF (.dif) file using Format Factory's DIF parser and writes each
row as an ODT paragraph using Format Factory's ODT writer.

Each DIF data row becomes one ODT paragraph, with cell values joined by a
configurable separator.

Sprint: DIF-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-DIF-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from dif.dif_parser import parse_dif_strict  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def dif_to_odt(
    dif_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = "\t",
    skip_empty_rows: bool = True,
) -> int:
    """Convert a DIF file to an ODT document, one paragraph per DIF row.

    Args:
        dif_path: Path to the source .dif file.
        dest_path: Path for the output .odt file (parent dirs created).
        separator: String used to join cell values within each paragraph.
        skip_empty_rows: When True, rows where all cells are empty are omitted.

    Returns:
        Number of paragraphs written.
    """
    dif_path = Path(dif_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_dif_strict(dif_path)  # Format Factory dif reader

    paragraphs: list[str] = []
    for dif_row in doc.rows:
        # DIF string values are stored with surrounding quotes — strip them
        parts: list[str] = []
        for cell in dif_row:
            raw = str(cell.value) if cell.value is not None else ""
            if raw.startswith('"') and raw.endswith('"'):
                raw = raw[1:-1]
            parts.append(raw)
        if skip_empty_rows and all(p == "" for p in parts):
            continue
        paragraphs.append(separator.join(parts))

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["dif_to_odt"]
