"""
ods_row_iterator.py — Spec-shaped row iteration for ODS documents.

Authority: ODF 1.3 §9.4 — table:table-row.
Spec QName: table:table-row (urn:oasis:names:tc:opendocument:xmlns:table:1.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .ods_parser import parse_ods
from .spec.table.table_row import TableRow


def ods_iter_rows(source: "str | Path") -> Iterator[TableRow]:
    """Yield spec-shaped TableRow objects for every row across all sheets in an ODS document.

    Args:
        source: Path to a .ods OpenDocument Spreadsheet file.

    Yields:
        TableRow instances (spec class: table:table-row, SAL-ODS-00001).
    """
    model = parse_ods(str(Path(source).resolve()))
    for sheet in model.get("sheets", []):
        for row in sheet.get("rows", []):
            if isinstance(row, dict):
                yield TableRow(row)
