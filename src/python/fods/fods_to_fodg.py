"""
fods_to_fodg.py — Dogfood export: FODS → FODG using Format Factory libraries.

Sprint: FODS-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-FODS-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from fods.parser import parse_fods_strict  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def fods_to_fodg(
    fods_path: str | Path,
    dest_path: str | Path,
    *,
    sheet_index: int = 0,
) -> int:
    """Convert a FODS flat spreadsheet to a FODG drawing, one page per row."""
    fods_path = Path(fods_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_fods_strict(fods_path)  # Format Factory fods reader
    sheets = doc.get("sheets", []) if isinstance(doc, dict) else []

    pages_list = []
    if sheets and sheet_index < len(sheets):
        sheet = sheets[sheet_index]
        for i, row in enumerate(sheet.get("rows", [])):
            texts = [
                str(c.get("value", "")) for c in row.get("cells", [])
                if c.get("value") is not None
            ]
            pages_list.append({"name": f"Row{i + 1}", "texts": texts})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["fods_to_fodg"]
