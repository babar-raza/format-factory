"""
abw_to_odt.py — Dogfood export: ABW → ODT using Format Factory libraries.

Reads an AbiWord (.abw) file using Format Factory's ABW codec and writes each
paragraph as an ODT paragraph using Format Factory's ODT writer.

Each ABW paragraph becomes one ODT paragraph.

Sprint: ABW-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "abw"))

from abw.abw_codec import load  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def abw_to_odt(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert an ABW file to an ODT document, one paragraph per ABW paragraph.

    Args:
        abw_path: Path to the source .abw file.
        dest_path: Path for the output .odt file (parent dirs created).
        skip_empty: When True, empty paragraphs are omitted.

    Returns:
        Number of paragraphs written.
    """
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load(abw_path)  # Format Factory abw reader
    raw_paragraphs = model.get("paragraphs", []) or []

    paragraphs: list[str] = []
    for para in raw_paragraphs:
        text = para.get("text", "") if isinstance(para, dict) else str(para)
        if skip_empty and not text:
            continue
        paragraphs.append(text)

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["abw_to_odt"]
