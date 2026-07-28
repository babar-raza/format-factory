"""
odt_to_dif.py — Dogfood export: ODT → DIF using Format Factory libraries.

Sprint: ODT-TO-DIF-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-DIF-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import OdtHeading, parse_odt_strict  # FF source reader
from dif.dif_parser import DifCell, DifDocument, write_dif  # FF target writer


def odt_to_dif(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
    title: str = "ODT Export",
) -> int:
    """Convert an ODT document to a DIF file, one row per element (type, text)."""
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader

    dif_rows = []
    for elem in doc.elements:
        text = elem.text if elem.text else ""
        if skip_empty and not text.strip():
            continue
        elem_type = "heading" if isinstance(elem, OdtHeading) else "paragraph"
        dif_rows.append([
            DifCell(value=elem_type, value_type="string"),
            DifCell(value=text, value_type="string"),
        ])

    dif_doc = DifDocument(title=title, rows=dif_rows)
    write_dif(dif_doc, dest_path)  # Format Factory dif writer
    return len(dif_rows)


__all__ = ["odt_to_dif"]
