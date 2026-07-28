"""
odt_to_fodg.py — Dogfood export: ODT → FODG using Format Factory libraries.

Sprint: ODT-TO-FODG-DOGFOOD-001
Authority: TASK-007 -- Advance one dogfood export path
Ledger entry: R90-ODT-TO-FODG-DOGFOOD-001
License: Apache-2.0
"""
from __future__ import annotations

from pathlib import Path

from odt.odt_parser import OdtHeading, parse_odt_strict  # FF source reader
from fodg.fodg_codec import create_fodg, write_fodg  # FF target writer


def odt_to_fodg(
    odt_path: str | Path,
    dest_path: str | Path,
    *,
    skip_empty: bool = True,
) -> int:
    """Convert an ODT document to a FODG drawing, one page per element."""
    odt_path = Path(odt_path)
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    doc = parse_odt_strict(odt_path)  # Format Factory odt reader

    pages_list = []
    for i, elem in enumerate(doc.elements):
        text = elem.text if elem.text else ""
        if skip_empty and not text.strip():
            continue
        elem_type = "heading" if isinstance(elem, OdtHeading) else "paragraph"
        pages_list.append({"name": f"{elem_type}{i + 1}", "texts": [elem_type, text]})

    model = create_fodg(pages_list)
    write_fodg(model, dest_path)  # Format Factory fodg writer
    return len(pages_list)


__all__ = ["odt_to_fodg"]
