"""
fods_sheet_iterator.py — Spec-shaped sheet iteration for FODS documents.

Authority: ODF 1.3 §9.1 — table:table.
Spec QName: table:table (urn:oasis:names:tc:opendocument:xmlns:table:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .models import FodsSheet
from .parser import parse_fods


def fods_iter_sheets(source: "str | Path") -> Iterator[FodsSheet]:
    """Yield spec-shaped FodsSheet objects for every sheet in a FODS document.

    Args:
        source: Path to a .fods flat XML OpenDocument Spreadsheet file.

    Yields:
        FodsSheet instances (spec class: table:table, FACT-FODS-004).
    """
    model = parse_fods(str(Path(source).resolve()))
    for sheet in model.get("sheets", []):
        yield FodsSheet(sheet)
