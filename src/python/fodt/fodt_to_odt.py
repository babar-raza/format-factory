"""
fodt_to_odt.py — Dogfood export: FODT → ODT using Format Factory libraries.

Reads a Flat OpenDocument Text (.fodt) file using Format Factory's FODT parser
and writes each block as an ODT paragraph using Format Factory's ODT writer.

This converts a flat single-XML ODF text file to a zipped ODF text container.
Each FODT block (paragraph or heading) becomes one ODT paragraph.

Sprint: FODT-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodt.parser import parse_fodt  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def fodt_to_odt(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert a FODT file to an ODT document.

    Each FODT block (paragraph or heading) becomes one ODT paragraph.

    Args:
        fodt_path: Path to the source .fodt file.
        dest_path: Path for the output .odt file (parent dirs created).
        skip_empty: When True, blocks with empty text are omitted.

    Returns:
        Number of paragraphs written.
    """
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    paragraphs: list[str] = []
    for block in blocks:
        text = block.get("text", "")
        if skip_empty and not text:
            continue
        paragraphs.append(text)

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["fodt_to_odt"]
