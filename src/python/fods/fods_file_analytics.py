"""
FODS file-path based analytics — supplementary file-path analytics functions.

Extends fods_analytics_extended.py with file-path based convenience functions.
Uses parse_fods_strict from fods.parser.
"""
from __future__ import annotations

from pathlib import Path

from .parser import parse_fods_strict

spec_qname = "fods:spreadsheet"
spec_fact_ref = "SAL-FODS-00001"


def fods_file_sheet_count(source: "str | Path") -> int:
    """Return the number of sheets in the FODS file.

    Spec: ODF 1.3 table:table element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return len(wb.get("sheets", []))


def fods_file_is_fods(source: "str | Path") -> bool:
    """Return True if the document is identified as a valid FODS file.

    Spec: ODF 1.3 MIME type application/vnd.oasis.opendocument.spreadsheet-flat-xml
    (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return wb.get("format_id", "") == "fods"


def fods_file_first_sheet_name(source: "str | Path") -> str:
    """Return the name of the first sheet. Empty string if no sheets.

    Spec: ODF 1.3 table:table@table:name (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    sheets = wb.get("sheets", [])
    return sheets[0].get("name", "") if sheets else ""


def fods_file_sheet_names(source: "str | Path") -> list:
    """Return list of sheet names in workbook order.

    Spec: ODF 1.3 table:table@table:name (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return [s.get("name", "") for s in wb.get("sheets", [])]


def fods_file_has_multiple_sheets(source: "str | Path") -> bool:
    """Return True if the FODS workbook contains more than one sheet.

    Spec: ODF 1.3 table:table element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return len(wb.get("sheets", [])) > 1


def fods_file_total_rows(source: "str | Path") -> int:
    """Return total row count across all sheets in the FODS file.

    Spec: ODF 1.3 table:table-row element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return sum(len(s.get("rows", [])) for s in wb.get("sheets", []))


def fods_file_has_parse_errors(source: "str | Path") -> bool:
    """Return True if the FODS file produced any parse errors during loading.

    Spec: ODF 1.3 table:table element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return bool(wb.get("parse_errors", []))


def fods_file_odf_version(source: "str | Path") -> str:
    """Return the ODF version attribute string from the FODS document.

    Spec: ODF 1.3 office:document@office:version (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return str(wb.get("odf_version_attr", ""))


def fods_file_has_warnings(source: "str | Path") -> bool:
    """Return True if the FODS parser emitted any warnings.

    Spec: ODF 1.3 table:table element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return bool(wb.get("warnings", []))


def fods_file_last_sheet_name(source: "str | Path") -> str:
    """Return the name of the last sheet. Empty string if no sheets.

    Spec: ODF 1.3 table:table@table:name (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    sheets = wb.get("sheets", [])
    return sheets[-1].get("name", "") if sheets else ""


def fods_file_sheet_row_counts(source: "str | Path") -> list:
    """Return list of row counts per sheet in workbook order.

    Spec: ODF 1.3 table:table-row element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return [s.get("row_count", 0) for s in wb.get("sheets", [])]


def fods_file_max_sheet_row_count(source: "str | Path") -> int:
    """Return the maximum row count across all sheets. 0 if no sheets.

    Spec: ODF 1.3 table:table-row element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    sheets = wb.get("sheets", [])
    if not sheets:
        return 0
    return max(s.get("row_count", 0) for s in sheets)


def fods_file_min_sheet_row_count(source: "str | Path") -> int:
    """Return the minimum row count across all sheets. 0 if no sheets.

    Spec: ODF 1.3 table:table-row element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    sheets = wb.get("sheets", [])
    if not sheets:
        return 0
    return min(s.get("row_count", 0) for s in sheets)


def fods_file_avg_sheet_row_count(source: "str | Path") -> float:
    """Return the average row count per sheet. 0.0 if no sheets.

    Spec: ODF 1.3 table:table-row element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    sheets = wb.get("sheets", [])
    if not sheets:
        return 0.0
    return sum(s.get("row_count", 0) for s in sheets) / len(sheets)


def fods_file_has_single_sheet(source: "str | Path") -> bool:
    """Return True if the FODS workbook contains exactly one sheet.

    Spec: ODF 1.3 table:table element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return len(wb.get("sheets", [])) == 1


def fods_file_sheet_names_sorted(source: "str | Path") -> list:
    """Return alphabetically sorted list of sheet names.

    Spec: ODF 1.3 table:table@table:name (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    return sorted(s.get("name", "") for s in wb.get("sheets", []))


def fods_file_first_sheet_row_count(source: "str | Path") -> int:
    """Return the row count of the first sheet. 0 if no sheets.

    Spec: ODF 1.3 table:table-row element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    sheets = wb.get("sheets", [])
    if not sheets:
        return 0
    return sheets[0].get("row_count", 0)


def fods_file_last_sheet_row_count(source: "str | Path") -> int:
    """Return the row count of the last sheet. 0 if no sheets.

    Spec: ODF 1.3 table:table-row element (SAL-FODS-00001)
    """
    wb = parse_fods_strict(source)
    sheets = wb.get("sheets", [])
    if not sheets:
        return 0
    return sheets[-1].get("row_count", 0)
