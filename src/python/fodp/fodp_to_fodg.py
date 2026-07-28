"""
fodp_to_fodg.py — Dogfood export: FODP → FODG using Format Factory libraries.

Sprint: FODP-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodp.fodp_codec import load as load_fodp  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def fodp_to_fodg(
    fodp_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a FODP presentation to a FODG drawing, one page per slide."""
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    slides = doc.get("pages", [])

    pages_list = []
    for slide in slides:
        slide_name = slide.get("name", "") or ""
        title_val = slide.get("title", "") or ""
        text_parts = slide.get("text_content", []) or []
        texts = [t for t in [slide_name, title_val] + [str(t) for t in text_parts] if t]
        pages_list.append({"name": slide_name or "Slide", "texts": texts})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["fodp_to_fodg"]
