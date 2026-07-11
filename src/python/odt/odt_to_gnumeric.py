"""
odt_to_gnumeric.py — Dogfood export: ODT → Gnumeric using Format Factory libraries.

Sprint: ODT-TO-GNUMERIC-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-GNUMERIC-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python" / "odt"))
sys.path.insert(0, str(_REPO))

from odt.odt_parser import OdtHeading, parse_odt_strict  # FF source reader
from gnumeric.gnumeric_codec import write_gnumeric  # FF target writer


def odt_to_gnumeric(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
    sheet_name: str = "Sheet1",
) -> int:
    """Convert ODT to a Gnumeric spreadsheet, one row per element (element_type, text)."""
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader

    cell_grid: dict = {}
    r = 0
    for elem in doc.elements:
        text = elem.text if elem.text else ""
        if skip_empty and not text.strip():
            continue
        elem_type = "heading" if isinstance(elem, OdtHeading) else "paragraph"
        cell_grid[(r, 0)] = elem_type
        cell_grid[(r, 1)] = text
        r += 1

    model = {"is_gnumeric": True, "sheets": [{"name": sheet_name, "cell_grid": cell_grid, "cell_count": len(cell_grid)}]}
    write_gnumeric(model, dest_path)  # Format Factory gnumeric writer
    return r


__all__ = ["odt_to_gnumeric"]
