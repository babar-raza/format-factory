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
