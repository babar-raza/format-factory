"""
fodt_to_gnumeric.py — Dogfood export: FODT → Gnumeric using Format Factory libraries.

Sprint: FODT-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODT-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fodt.parser import parse_fodt  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def fodt_to_gnumeric(
    fodt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert FODT to a Gnumeric spreadsheet, one row per block (block_type, text)."""
    fodt_path = Path(fodt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fodt(str(fodt_path))  # Format Factory fodt reader
    blocks = doc.get("blocks", [])

    cell_grid: dict = {}
    r = 0
    for block in blocks:
        text = block.get("text", "") or ""
        if skip_empty and not text.strip():
            continue
        block_type = block.get("type", "paragraph") or "paragraph"
        cell_grid[(r, 0)] = block_type
        cell_grid[(r, 1)] = text
        r += 1

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return r


__all__ = ["fodt_to_gnumeric"]
