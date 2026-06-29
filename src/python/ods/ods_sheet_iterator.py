"""
ods_sheet_iterator.py — Spec-shaped sheet iteration for ODS documents.

Authority: ODF 1.3 Part 4 — Spreadsheet (table:table).
Spec QName: table:table (urn:oasis:names:tc:opendocument:xmlns:table:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .ods_parser import parse_ods
from .spec.table.table import Table


def ods_iter_sheets(source: "str | Path") -> Iterator[Table]:
    """Yield spec-shaped Table objects for every sheet in an ODS document.

    Args:
        source: Path to an .ods OpenDocument Spreadsheet file.

    Yields:
        Table instances (spec class: table:table, FACT-ODS-001).
    """
    model = parse_ods(str(Path(source).resolve()))
    for sheet in model.get("sheets", []):
        yield Table(sheet)
