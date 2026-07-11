"""
Gnumeric sheet analytics — file-path based workbook statistics.

Extends gnumeric_analytics.py with analytics based on sheet metadata.
Uses load and get_sheet_metadata from gnumeric_codec.
"""
from __future__ import annotations

from pathlib import Path

from .gnumeric_codec import load, get_sheet_metadata, extract_values

spec_qname = "gnumeric:workbook"
spec_fact_ref = "FACT-GNUMERIC-001"


def gnumeric_has_single_sheet(source: "str | bytes | Path") -> bool:
    """Return True if the workbook contains exactly one sheet."""
    doc = load(source)
    return doc.get("sheet_count", 0) == 1


def gnumeric_sheet_names_list(source: "str | bytes | Path") -> list:
    """Return list of sheet names in workbook order."""
    meta = get_sheet_metadata(source)
    return [s.get("name", "") for s in meta]


def gnumeric_is_empty_workbook(source: "str | bytes | Path") -> bool:
    """Return True if the workbook contains no cell data across all sheets."""
    doc = load(source)
    return doc.get("cell_count", 0) == 0


def gnumeric_sheets_with_data_count(source: "str | bytes | Path") -> int:
    """Return count of sheets that have at least one cell value."""
    meta = get_sheet_metadata(source)
    return sum(1 for s in meta if s.get("cell_count", 0) > 0)


def gnumeric_total_unique_value_count(source: "str | bytes | Path") -> int:
    """Return count of distinct cell values across the entire workbook."""
    values = extract_values(source)
    return len(set(values))


def gnumeric_has_numeric_values(source: "str | bytes | Path") -> bool:
    """Return True if any cell value in the workbook is a valid numeric string."""
    values = extract_values(source)
    for v in values:
        try:
            float(v)
            return True
        except (ValueError, TypeError):
            pass
    return False


def gnumeric_sheet_count(source: "str | bytes | Path") -> int:
    """Return the total number of sheets in the workbook.

    Spec: Gnumeric workbook gnm:Sheet element (FACT-GNUMERIC-001)
    """
    doc = load(source)
    return doc.get("sheet_count", 0)


def gnumeric_is_gnumeric(source: "str | bytes | Path") -> bool:
    """Return True if the document is identified as a valid Gnumeric file.

    Spec: Gnumeric workbook format (FACT-GNUMERIC-001)
    """
    doc = load(source)
    return bool(doc.get("is_gnumeric", False))


def gnumeric_cell_count(source: "str | bytes | Path") -> int:
    """Return total cell count across all sheets in the workbook.

    Spec: Gnumeric workbook gnm:Cell element (FACT-GNUMERIC-001)
    """
    doc = load(source)
    return doc.get("cell_count", 0)


def gnumeric_first_sheet_name(source: "str | bytes | Path") -> str:
    """Return the name of the first sheet, or empty string if no sheets.

    Spec: Gnumeric workbook gnm:Sheet element (FACT-GNUMERIC-001)
    """
    meta = get_sheet_metadata(source)
    return meta[0].get("name", "") if meta else ""


def gnumeric_first_sheet_cell_count(source: "str | bytes | Path") -> int:
    """Return the cell count of the first sheet. 0 if no sheets.

    Spec: Gnumeric workbook gnm:Cell element (FACT-GNUMERIC-001)
    """
    meta = get_sheet_metadata(source)
    return meta[0].get("cell_count", 0) if meta else 0


def gnumeric_all_values(source: "str | bytes | Path") -> list:
    """Return a flat list of all cell values across all sheets in workbook order.

    Spec: Gnumeric workbook gnm:Cell element (FACT-GNUMERIC-001)
    """
    return list(extract_values(source))


def gnumeric_has_data(source: "str | bytes | Path") -> bool:
    """Return True if the workbook contains at least one cell.

    Spec: Gnumeric workbook gnm:Cell element (FACT-GNUMERIC-001)
    """
    doc = load(source)
    return doc.get("cell_count", 0) > 0


def gnumeric_unique_value_count(source: "str | bytes | Path") -> int:
    """Return count of distinct string cell values in the workbook.

    Spec: Gnumeric workbook gnm:Cell element (FACT-GNUMERIC-001)
    """
    return len(set(extract_values(source)))


def gnumeric_sheet_names_sorted(source: "str | bytes | Path") -> list:
    """Return alphabetically sorted list of sheet names.

    Spec: Gnumeric workbook gnm:Sheet element (FACT-GNUMERIC-001)
    """
    meta = get_sheet_metadata(source)
    return sorted(s.get("name", "") for s in meta)


def gnumeric_total_value_count(source: "str | bytes | Path") -> int:
    """Return count of all cell values (not unique) across the workbook.

    Spec: Gnumeric workbook gnm:Cell element (FACT-GNUMERIC-001)
    """
    return len(list(extract_values(source)))


def gnumeric_has_multiple_sheets(source: "str | bytes | Path") -> bool:
    """Return True if the workbook contains more than one sheet.

    Spec: Gnumeric workbook gnm:Sheet element (FACT-GNUMERIC-001)
    """
    doc = load(source)
    return doc.get("sheet_count", 0) > 1


def gnumeric_max_sheet_cell_count(source: "str | bytes | Path") -> int:
    """Return the cell count of the sheet with the most cells. 0 if no sheets.

    Spec: Gnumeric workbook gnm:Cell element (FACT-GNUMERIC-001)
    """
    meta = get_sheet_metadata(source)
    if not meta:
        return 0
    return max(s.get("cell_count", 0) for s in meta)
