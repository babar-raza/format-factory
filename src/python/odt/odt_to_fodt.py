"""
odt_to_fodt.py — Dogfood export: ODT → FODT using Format Factory libraries.

Reads an OpenDocument Text (.odt) file using Format Factory's ODT parser
and writes each element as a FODT block using Format Factory's FODT writer.

Each ODT element (paragraph, heading, list item) becomes one FODT block,
preserving the element type (paragraph → text:p, heading → text:h).

Sprint: ODT-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import OdtHeading, OdtListItem, parse_odt_strict  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def odt_to_fodt(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert an ODT file to a FODT flat text document.

    Each ODT element becomes a FODT block. Headings become 'heading' type blocks;
    paragraphs and list items become 'paragraph' type blocks.

    Args:
        odt_path: Path to the source .odt file.
        dest_path: Path for the output .fodt file (parent dirs created).
        skip_empty: When True, elements with empty text are omitted.

    Returns:
        Number of FODT blocks written.
    """
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader
    elements = doc.elements

    blocks: list[dict] = []
    for elem in elements:
        text = elem.text if elem.text else ""
        if skip_empty and not text.strip():
            continue
        if isinstance(elem, OdtHeading):
            blocks.append({"type": "heading", "text": text})
        else:
            blocks.append({"type": "paragraph", "text": text})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["odt_to_fodt"]
