"""
fodp_to_odt.py — Dogfood export: FODP → ODT using Format Factory libraries.

Reads a Flat OpenDocument Presentation (.fodp) file using Format Factory's
FODP codec and writes each slide as an ODT paragraph using Format Factory's
ODT writer.

Each slide becomes one paragraph: "slide_name: title — text_content".

Sprint: FODP-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodp"))
sys.path.insert(0, str(_REPO))

from fodp.fodp_codec import load as load_fodp  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def fodp_to_odt(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    include_slide_index: bool = False,
) -> int:
    """Convert a FODP presentation to an ODT document, one paragraph per slide.

    Args:
        fodp_path: Path to the source .fodp file.
        dest_path: Path for the output .odt file (parent dirs created).
        include_slide_index: When True, prepends slide index to each paragraph.

    Returns:
        Number of paragraphs written.
    """
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    paragraphs: list[str] = []
    for idx, page in enumerate(pages):
        slide_name = page.get("name", "") or ""
        title = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)

        parts: list[str] = []
        if include_slide_index:
            parts.append(str(idx))
        if slide_name:
            parts.append(slide_name)
        if title:
            parts.append(title)
        if text_content:
            parts.append(text_content)
        paragraphs.append(" — ".join(parts) if parts else "")

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["fodp_to_odt"]
