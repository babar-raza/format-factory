"""
FODS file-path based analytics — supplementary file-path analytics functions.

Extends fods_analytics_extended.py with file-path based convenience functions.
Uses parse_fods_strict from fods.parser.
"""
from __future__ import annotations

from pathlib import Path

from .parser import parse_fods_strict

spec_qname = "fods:spreadsheet"
spec_fact_ref = "FACT-FODS-001"


def fods_file_sheet_count(source: "str | Path") -> int:
    """Return the number of sheets in the FODS file.

    Spec: ODF 1.3 table:table element (FACT-FODS-001)
    """
    wb = parse_fods_strict(source)
    return len(wb.get("sheets", []))


def fods_file_is_fods(source: "str | Path") -> bool:
    """Return True if the document is identified as a valid FODS file.

    Spec: ODF 1.3 MIME type application/vnd.oasis.opendocument.spreadsheet-flat-xml
    (FACT-FODS-001)
    """
    wb = parse_fods_strict(source)
    return wb.get("format_id", "") == "fods"


def fods_file_first_sheet_name(source: "str | Path") -> str:
    """Return the name of the first sheet. Empty string if no sheets.

    Spec: ODF 1.3 table:table@table:name (FACT-FODS-001)
    """
    wb = parse_fods_strict(source)
    sheets = wb.get("sheets", [])
    return sheets[0].get("name", "") if sheets else ""


def fods_file_sheet_names(source: "str | Path") -> list:
    """Return list of sheet names in workbook order.

    Spec: ODF 1.3 table:table@table:name (FACT-FODS-001)
    """
    wb = parse_fods_strict(source)
    return [s.get("name", "") for s in wb.get("sheets", [])]


def fods_file_has_multiple_sheets(source: "str | Path") -> bool:
    """Return True if the FODS workbook contains more than one sheet.

    Spec: ODF 1.3 table:table element (FACT-FODS-001)
    """
    wb = parse_fods_strict(source)
    return len(wb.get("sheets", [])) > 1


def fods_file_total_rows(source: "str | Path") -> int:
    """Return total row count across all sheets in the FODS file.

    Spec: ODF 1.3 table:table-row element (FACT-FODS-001)
    """
    wb = parse_fods_strict(source)
    return sum(len(s.get("rows", [])) for s in wb.get("sheets", []))
