"""
abw_to_gnumeric.py — Dogfood export: ABW → Gnumeric using Format Factory libraries.

Sprint: ABW-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ABW-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import load as load_abw  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def abw_to_gnumeric(
    abw_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert ABW to a Gnumeric spreadsheet, one row per paragraph."""
    abw_path = Path(abw_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_abw(abw_path)  # Format Factory abw reader
    paragraphs = model.get("paragraphs", [])

    cell_grid: dict = {}
    for r, para in enumerate(paragraphs):
        text = para.get("text", "") if isinstance(para, dict) else str(para)
        cell_grid[(r, 0)] = text

    gnumeric_model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(gnumeric_model, dest_path)  # Format Factory gnumeric writer
    return len(paragraphs)


__all__ = ["abw_to_gnumeric"]
