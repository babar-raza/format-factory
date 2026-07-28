"""
fodg_to_odt.py — Dogfood export: FODG → ODT using Format Factory libraries.

Reads a Flat OpenDocument Drawing (.fodg) file using Format Factory's FODG
codec and writes each page as an ODT paragraph using Format Factory's ODT writer.

Each drawing page becomes one paragraph with page_name and text_content joined.

Sprint: FODG-TO-ODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-ODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodg.fodg_codec import load as load_fodg  # FF source reader
from odt.odt_writer import write_odt  # FF target writer


def fodg_to_odt(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    include_page_index: bool = False,
) -> int:
    """Convert a FODG drawing file to an ODT document, one paragraph per page.

    Args:
        fodg_path: Path to the source .fodg file.
        dest_path: Path for the output .odt file (parent dirs created).
        include_page_index: When True, prepends page index to each paragraph.

    Returns:
        Number of paragraphs written.
    """
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    paragraphs: list[str] = []
    for idx, page in enumerate(pages):
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)

        parts: list[str] = []
        if include_page_index:
            parts.append(str(idx))
        if page_name:
            parts.append(page_name)
        if text_content:
            parts.append(text_content)
        paragraphs.append(" — ".join(parts) if parts else "")

    write_odt(paragraphs, dest_path)  # Format Factory odt writer
    return len(paragraphs)


__all__ = ["fodg_to_odt"]
