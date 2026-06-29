"""
gnumeric_sheet_iterator.py — Spec-shaped sheet iteration for Gnumeric documents.

Authority: Gnumeric XML format — gnm:Sheet element.
Spec QName: gnumeric:sheet (http://www.gnumeric.org/v10.dtd)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .gnumeric_codec import load
from .spec.workbook.sheet import Sheet


def gnumeric_iter_sheets(source: "str | Path") -> Iterator[Sheet]:
    """Yield spec-shaped Sheet objects for every sheet in a Gnumeric document.

    Args:
        source: Path to a .gnumeric Gnumeric spreadsheet file.

    Yields:
        Sheet instances (spec class: gnumeric:sheet, FACT-GNUMERIC-002).
    """
    model = load(str(Path(source).resolve()))
    for sheet_dict in model.get("sheets", []):
        if isinstance(sheet_dict, dict):
            yield Sheet(sheet_dict)
