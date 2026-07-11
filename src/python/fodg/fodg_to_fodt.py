"""
fodg_to_fodt.py — Dogfood export: FODG → FODT using Format Factory libraries.

Reads a Flat OpenDocument Drawing (.fodg) file using Format Factory's FODG
codec and writes each drawing page as a FODT paragraph using Format Factory's
FODT writer.

Each FODG page becomes one FODT paragraph summarizing the page content.

Sprint: FODG-TO-FODT-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-FODT-DOGFOOD-001

License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodg"))
sys.path.insert(0, str(_REPO))

from fodg.fodg_codec import load as load_fodg  # FF source reader
from fodt.writer import write_fodt  # FF target writer


def fodg_to_fodt(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    separator: str = " — ",
) -> int:
    """Convert a FODG drawing file to a FODT document, one paragraph per page.

    Each drawing page becomes one FODT paragraph combining the page name and
    text content, joined with the separator.

    Args:
        fodg_path: Path to the source .fodg file.
        dest_path: Path for the output .fodt file (parent dirs created).
        separator: String used to join page parts (name, text).

    Returns:
        Number of FODT paragraphs written.
    """
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    blocks: list[dict] = []
    for page in pages:
        parts: list[str] = []
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = " ".join(str(t) for t in text_parts if t)
        if page_name:
            parts.append(page_name)
        if text_content:
            parts.append(text_content)
        blocks.append({"type": "paragraph", "text": separator.join(parts) if parts else ""})

    write_fodt({"blocks": blocks}, dest_path)  # Format Factory fodt writer
    return len(blocks)


__all__ = ["fodg_to_fodt"]
