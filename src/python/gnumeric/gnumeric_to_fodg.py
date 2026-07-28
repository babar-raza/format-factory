"""
gnumeric_to_fodg.py — Dogfood export: Gnumeric → FODG using Format Factory libraries.

Sprint: GNUMERIC-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-GNUMERIC-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from gnumeric.gnumeric_codec import load as load_gnumeric  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def gnumeric_to_fodg(
    gnumeric_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert a Gnumeric spreadsheet to a FODG drawing, one page per row."""
    gnumeric_path = Path(gnumeric_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = load_gnumeric(gnumeric_path)  # Format Factory gnumeric reader
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []

    pages_list = []
    if sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        cell_grid = sheet.get("cell_grid", {})
        rows: dict[int, list] = {}
        for (r0, c0), val in cell_grid.items():
            rows.setdefault(r0, []).append((c0, str(val)))
        for r0 in sorted(rows):
            texts = [v for _, v in sorted(rows[r0])]
            pages_list.append({"name": f"Row{r0 + 1}", "texts": texts})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["gnumeric_to_fodg"]
