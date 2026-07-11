"""
fodg_to_gnumeric.py — Dogfood export: FODG → Gnumeric using Format Factory libraries.

Sprint: FODG-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODG-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "fodg"))
sys.path.insert(0, str(_REPO))

from fodg.fodg_codec import load as load_fodg  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def fodg_to_gnumeric(
    fodg_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert FODG to a Gnumeric spreadsheet, one row per page (name, text, shape_count)."""
    fodg_path = Path(fodg_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_fodg(fodg_path)  # Format Factory fodg reader
    pages = doc.get("pages", [])

    cell_grid: dict = {}
    for r, page in enumerate(pages):
        page_name = page.get("name", "") or ""
        text_parts = page.get("text_content", []) or []
        text_content = " ".join(str(t) for t in text_parts if t)
        shape_count = str(page.get("shape_count", 0))
        cell_grid[(r, 0)] = page_name
        cell_grid[(r, 1)] = text_content
        cell_grid[(r, 2)] = shape_count

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return len(pages)


__all__ = ["fodg_to_gnumeric"]
