"""
fodt_to_abw.py — Dogfood export: FODT → ABW using Format Factory libraries.

Reads a FODT file using Format Factory's FODT parser and writes each block
as an ABW paragraph using Format Factory's ABW writer.

Each FODT block becomes one ABW paragraph.

Sprint: FODT-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodt"))
sys.path.insert(0, str(_REPO))

from fodt.parser import parse_fodt  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def fodt_to_abw(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert a FODT file to an ABW document, one paragraph per block.

    Each FODT block (paragraph or heading) becomes one ABW paragraph.

    Args:
        fodt_path: Path to the source .fodt file.
        dest_path: Path for the output .abw file (parent dirs created).
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
        text = block.get("text", "") or ""
        if skip_empty and not text.strip():
            continue
        paragraphs.append(text)

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["fodt_to_abw"]
