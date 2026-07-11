"""
abw_to_fodt.py — Dogfood export: ABW → FODT using Format Factory libraries.

Reads an ABW file using Format Factory's ABW codec and writes each paragraph
as a FODT paragraph using Format Factory's FODT writer.

Each ABW paragraph becomes one FODT paragraph preserving the text content.

Sprint: ABW-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import load as load_abw  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def abw_to_fodt(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert an ABW file to a FODT flat text document, one paragraph per ABW block.

    Each ABW paragraph becomes one FODT paragraph preserving its text content.

    Args:
        abw_path: Path to the source .abw file.
        dest_path: Path for the output .fodt file (parent dirs created).
        skip_empty: When True, ABW paragraphs with no text are skipped.

    Returns:
        Number of FODT paragraphs written.
    """
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_abw(abw_path)  # Format Factory abw reader
    paragraphs = model.get("paragraphs", [])

    blocks: list[dict] = []
    for para in paragraphs:
        text = para.get("text", "") if isinstance(para, dict) else str(para)
        if skip_empty and not text.strip():
            continue
        blocks.append({"type": "paragraph", "text": text})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["abw_to_fodt"]
