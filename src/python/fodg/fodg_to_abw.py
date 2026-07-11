"""
fodg_to_abw.py — Dogfood export: FODG → ABW using Format Factory libraries.

Reads a FODG file using Format Factory's FODG codec and writes each drawing
page as an ABW paragraph using Format Factory's ABW writer.

Each FODG page becomes one ABW paragraph summarizing the page content.

Sprint: FODG-TO-ABW-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-ABW-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodg"))
sys.path.insert(0, str(_REPO))

from fodg.fodg_codec import load as load_fodg  # FF source reader
from abw.abw_codec import write_abw  # FF target writer


def fodg_to_abw(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " — ",
) -> int:
    """Convert a FODG drawing file to an ABW document, one paragraph per page.

    Each page becomes one ABW paragraph combining page name and text content
    joined with the separator.

    Args:
        fodg_path: Path to the source .fodg file.
        dest_path: Path for the output .abw file (parent dirs created).
        separator: String used to join page parts.

    Returns:
        Number of paragraphs (pages) written.
    """
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    paragraphs: list[str] = []
    for page in pages:
        parts: list[str] = []
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = " ".join(str(t) for t in text_parts if t)
        if page_name:
            parts.append(page_name)
        if text_content:
            parts.append(text_content)
        paragraphs.append(separator.join(parts) if parts else "")

    model = {"is_abw": True, "paragraphs": paragraphs}
    write_abw(model, dest_path)  # Format Factory abw writer
    return len(paragraphs)


__all__ = ["fodg_to_abw"]
