"""
odt_to_abw.py — Dogfood export: ODT → ABW using Format Factory libraries.

Reads an ODT file using Format Factory's ODT parser and writes each element
as an ABW paragraph using Format Factory's ABW writer.

Each ODT element (heading, paragraph, list item) becomes one ABW paragraph.

Sprint: ODT-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import parse_odt_strict  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def odt_to_abw(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert an ODT file to an ABW document, one paragraph per element.

    Each ODT element (heading, paragraph, list item) becomes one ABW paragraph.

    Args:
        odt_path: Path to the source .odt file.
        dest_path: Path for the output .abw file (parent dirs created).
        skip_empty: When True, elements with empty text are omitted.

    Returns:
        Number of paragraphs written.
    """
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader

    paragraphs: list[str] = []
    for elem in doc.elements:
        text = elem.text if elem.text else ""
        if skip_empty and not text.strip():
            continue
        paragraphs.append(text)

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["odt_to_abw"]
