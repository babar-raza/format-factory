"""
toml_to_sylk.py — Dogfood export: TOML → SYLK using Format Factory libraries.

Sprint: TOML-TO-SYLK-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-TOML-TO-SYLK-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from toml.toml_codec import load_toml  # FF source reader
from sylk.sylk_parser import SylkCell, SylkDocument, write_sylk  # FF target writer


def toml_to_sylk(
    toml_path: str | Path,
    dest_path: str | Path,
) -> int:
    """Convert a TOML file to a SYLK spreadsheet, one row per top-level key."""
    toml_path = Path(toml_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    data = load_toml(toml_path)  # Format Factory toml reader

    cells: list[SylkCell] = []
    items = data.items() if isinstance(data, dict) else []
    for r, (key, val) in enumerate(items, start=1):
        cells.append(SylkCell(row=r, col=1, value=str(key), value_type="string"))
        cells.append(SylkCell(row=r, col=2, value=str(val), value_type="string"))

    max_row = max((cell.row for cell in cells), default=0)
    sylk_doc = SylkDocument(cells=cells, rows=max_row, cols=2 if cells else 0)
    write_sylk(sylk_doc, dest_path)  # Format Factory sylk writer
    return max_row


__all__ = ["toml_to_sylk"]
