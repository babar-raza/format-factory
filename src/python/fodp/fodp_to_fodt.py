"""
fodp_to_fodt.py — Dogfood export: FODP → FODT using Format Factory libraries.

Reads a Flat OpenDocument Presentation (.fodp) file using Format Factory's
FODP codec and writes each slide as a FODT paragraph using Format Factory's
FODT writer.

Each FODP slide becomes one FODT paragraph summarizing the slide content.

Sprint: FODP-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodp.fodp_codec import load as load_fodp  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def fodp_to_fodt(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " — ",
) -> int:
    """Convert a FODP presentation to a FODT document, one paragraph per slide.

    Each slide becomes one FODT paragraph combining the slide name, title,
    and text content items, joined with the separator.

    Args:
        fodp_path: Path to the source .fodp file.
        dest_path: Path for the output .fodt file (parent dirs created).
        separator: String used to join slide parts (name, title, text).

    Returns:
        Number of FODT paragraphs written.
    """
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    blocks: list[dict] = []
    for page in pages:
        parts: list[str] = []
        slide_name = page.get("name", "") or ""
        title = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = " ".join(str(t) for t in text_parts if t)
        if slide_name:
            parts.append(slide_name)
        if title:
            parts.append(title)
        if text_content:
            parts.append(text_content)
        blocks.append({"type": "paragraph", "text": separator.join(parts)})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["fodp_to_fodt"]
