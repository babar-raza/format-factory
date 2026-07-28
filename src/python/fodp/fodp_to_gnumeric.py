"""
fodp_to_gnumeric.py — Dogfood export: FODP → Gnumeric using Format Factory libraries.

Sprint: FODP-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODP-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodp.fodp_codec import load as load_fodp  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def fodp_to_gnumeric(
    fodp_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert FODP to a Gnumeric spreadsheet, one row per slide (name, title, text)."""
    fodp_path = Path(fodp_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodp(fodp_path)  # Format Factory fodp reader
    pages = doc.get("pages", [])

    cell_grid: dict = {}
    for r, page in enumerate(pages):
        slide_name = page.get("name", "") or ""
        title = page.get("title", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = "; ".join(str(t) for t in text_parts if t)
        cell_grid[(r, 0)] = slide_name
        cell_grid[(r, 1)] = title
        cell_grid[(r, 2)] = text_content

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(pages)


__all__ = ["fodp_to_gnumeric"]
