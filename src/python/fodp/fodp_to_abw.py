"""
fodp_to_abw.py — Dogfood export: FODP → ABW using Format Factory libraries.

Reads a FODP file using Format Factory's FODP codec and writes each slide
as an ABW paragraph using Format Factory's ABW writer.

Each FODP slide becomes one ABW paragraph summarizing the slide content.

Sprint: FODP-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodp"))
sys.path.insert(0, str(_REPO))

from fodp.fodp_codec import load as load_fodp  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def fodp_to_abw(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " — ",
) -> int:
    """Convert a FODP presentation to an ABW document, one paragraph per slide.

    Each slide becomes one ABW paragraph combining slide name, title, and
    text content joined with the separator.

    Args:
        fodp_path: Path to the source .fodp file.
        dest_path: Path for the output .abw file (parent dirs created).
        separator: String used to join slide parts.

    Returns:
        Number of paragraphs (slides) written.
    """
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    paragraphs: list[str] = []
    for page in pages:
        parts: list[str] = []
        slide_name = page.get("name", "") or ""
        title = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = " ".join(str(t) for t in text_parts if t)
        if slide_name:
            parts.append(slide_name)
        if title and title != slide_name:
            parts.append(title)
        if text_content:
            parts.append(text_content)
        paragraphs.append(separator.join(parts) if parts else "")

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["fodp_to_abw"]
