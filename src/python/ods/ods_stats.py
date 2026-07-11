"""
ods_stats.py -- Statistics and analysis functions for ODS neutral model dicts.

Works on the dict output of parse_ods(), not on file paths.
All functions are pure: no I/O, no mutation.

Added in R62 (format track advancement).

License: Apache-2.0
Package: format-factory-ods v0.1.0
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def spreadsheet_stats(ods_doc: dict[str, Any]) -> dict[str, Any]:
    """Return aggregate statistics for an ODS spreadsheet dict.

    Works on the output of parse_ods().
    Returns:
        sheet_count (int), total_rows (int), total_cells (int),
        non_empty_cells (int), per_sheet (list[dict]).
    """
    sheets = ods_doc.get("sheets", [])
    total_rows = 0
    total_cells = 0
    non_empty_cells = 0
    per_sheet: list[dict[str, Any]] = []

    for sheet in sheets:
        s_rows = sheet.get("rows", [])
        s_cells = 0
        s_non_empty = 0
        for row in s_rows:
            cells = row.get("cells", [])
            s_cells += len(cells)
            for cell in cells:
                val = cell.get("value") or cell.get("text") or ""
                if val not in (None, "", 0) or str(val).strip():
                    s_non_empty += 1
        total_rows += len(s_rows)
        total_cells += s_cells
        non_empty_cells += s_non_empty
        per_sheet.append({
            "name": sheet.get("name", ""),
            "row_count": len(s_rows),
            "cell_count": s_cells,
            "non_empty_cells": s_non_empty,
        })

    return {
        "sheet_count": len(sheets),
        "total_rows": total_rows,
        "total_cells": total_cells,
        "non_empty_cells": non_empty_cells,
        "per_sheet": per_sheet,
    }


def sheet_name_order(ods_doc: dict[str, Any]) -> list[str]:
    """Return the ordered list of sheet names from an ODS document dict.

    """
    return [
        sheet.get("name", f"Sheet{i + 1}")
        for i, sheet in enumerate(ods_doc.get("sheets", []))
    ]


def ods_cell_type_distribution(ods_doc: dict) -> dict:
    """Return distribution of cell value types across the ODS document.

    Scans all cells and classifies each by whether it has text, a numeric
    value, is empty, or carries other content. Returns:
      by_type: dict[str, int]   — count per type label
      total_cells: int
      empty_fraction: float     — fraction of cells that are empty

    """
    by_type: dict[str, int] = {}
    total = 0
    for sheet in ods_doc.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                total += 1
                val = cell.get("value")
                text = cell.get("text") or ""
                if val is None and not text.strip():
                    label = "empty"
                elif isinstance(val, (int, float)):
                    label = "numeric"
                elif text.strip():
                    label = "text"
                else:
                    label = "other"
                by_type[label] = by_type.get(label, 0) + 1
    empty_count = by_type.get("empty", 0)
    return {
        "by_type": by_type,
        "total_cells": total,
        "empty_fraction": round(empty_count / total, 4) if total > 0 else 0.0,
    }


def ods_sheet_name_list(ods_doc: dict) -> list[str]:
    """Return the list of sheet names from an ODS document dict.

    Simple accessor that extracts sheet names in order. Differs from
    sheet_name_order() by returning an empty list (not raising) when
    the document has no sheets key at all.

    Returns:
        list[str] — ordered sheet names. Empty list if no sheets.

    """
    sheets = ods_doc.get("sheets", [])
    return [sheet.get("name", "") for sheet in sheets]


def ods_formula_cell_count(ods_doc: dict[str, Any]) -> int:
    """Return the count of cells containing formulas in the ODS document.

    Scans all sheets for cells that carry a 'formula' attribute (non-None).

    Args:
        ods_doc: Parsed ODS document dict (from parse_ods()).

    Returns:
        int — number of formula cells across all sheets. 0 if none.

    Useful for spreadsheet auditing and formula complexity assessment.
    """
    count = 0
    for sheet in ods_doc.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell.get("formula") is not None:
                    count += 1
    return count


def ods_data_validation_count(ods_doc: dict[str, Any]) -> int:
    """Return the count of data validation rules in the ODS document.

    Scans for data validation metadata stored in:
    - 'data_validations' list at document level
    - 'content_validations' or 'content-validations' lists
    - per-cell 'validation' or 'table:content-validation-name' attributes

    Args:
        ods_doc: Parsed ODS document dict (from parse_ods()).

    Returns:
        int -- number of data validation rules found. 0 if none.

    Useful for spreadsheet auditing and data integrity analysis.
    """
    count = 0

    # Check explicit validation lists at document level
    for key in ("data_validations", "content_validations", "content-validations"):
        validations = ods_doc.get(key)
        if isinstance(validations, list):
            count += len(validations)

    # If no explicit list found, scan cells for validation attributes
    if count == 0:
        seen: set[str] = set()
        for sheet in ods_doc.get("sheets", []):
            for row in sheet.get("rows", []):
                for cell in row.get("cells", []):
                    val_name = (
                        cell.get("validation")
                        or cell.get("table:content-validation-name")
                    )
                    if val_name and str(val_name) not in seen:
                        seen.add(str(val_name))
                        count += 1

    return count


# --- File-path based analytics ---

def _ods_load(file_path: "str | Path") -> dict[str, Any]:
    """Load an ODS file and return the parse_ods dict."""
    from .ods_parser import parse_ods
    return parse_ods(file_path)


def ods_has_data(file_path: "str | Path") -> bool:
    """Return True if any cell in the ODS file has a non-empty value.

    Args:
        file_path: Path to the .ods file.

    Returns:
        bool — True if at least one cell has a non-empty value or text.
    """
    doc = _ods_load(file_path)
    for sheet in doc.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                val = cell.get("value")
                text = cell.get("text", "")
                if val not in (None, "", 0) or (isinstance(text, str) and text.strip()):
                    return True
    return False


def ods_first_sheet_name(file_path: "str | Path") -> str:
    """Return the name of the first sheet in the ODS file.

    Args:
        file_path: Path to the .ods file.

    Returns:
        str — Name of the first sheet, or empty string if no sheets.
    """
    doc = _ods_load(file_path)
    sheets = doc.get("sheets", [])
    if not sheets:
        return ""
    return sheets[0].get("name", "")


def ods_total_row_count(file_path: "str | Path") -> int:
    """Return the total row count across all sheets in the ODS file.

    Args:
        file_path: Path to the .ods file.

    Returns:
        int — Sum of row_count for every sheet. 0 if no sheets or no rows.
    """
    doc = _ods_load(file_path)
    return sum(sheet.get("row_count", 0) for sheet in doc.get("sheets", []))


def ods_unique_sheet_names(file_path: "str | Path") -> list[str]:
    """Return a list of distinct sheet names from the ODS file.

    Args:
        file_path: Path to the .ods file.

    Returns:
        list[str] — Unique sheet names preserving first-occurrence order.
    """
    doc = _ods_load(file_path)
    seen: set[str] = set()
    result: list[str] = []
    for sheet in doc.get("sheets", []):
        name = sheet.get("name", "")
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def ods_has_float_cells(file_path: "str | Path") -> bool:
    """Return True if the ODS file contains at least one float/numeric cell.

    Args:
        file_path: Path to the .ods file.

    Returns:
        bool — True if any cell has value_type 'float', 'percentage', or 'currency'.
    """
    doc = _ods_load(file_path)
    float_types = {"float", "percentage", "currency"}
    for sheet in doc.get("sheets", []):
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                if cell.get("value_type", "") in float_types:
                    return True
    return False


def ods_max_sheet_row_count(file_path: "str | Path") -> int:
    """Return the maximum row count across all sheets in the ODS file.

    Args:
        file_path: Path to the .ods file.

    Returns:
        int — Maximum row_count of any single sheet. 0 if no sheets.
    """
    doc = _ods_load(file_path)
    sheets = doc.get("sheets", [])
    if not sheets:
        return 0
    return max(sheet.get("row_count", 0) for sheet in sheets)


def ods_sheet_names_sorted(file_path: "str | Path") -> list:
    """Return alphabetically sorted list of sheet names from the ODS file.

    Spec: ODS table:table element (FACT-ODS-001)
    """
    doc = _ods_load(file_path)
    return sorted(sheet.get("name", "") for sheet in doc.get("sheets", []))


def ods_has_single_sheet(file_path: "str | Path") -> bool:
    """Return True if the ODS file contains exactly one sheet.

    Spec: ODS table:table element (FACT-ODS-001)
    """
    doc = _ods_load(file_path)
    return len(doc.get("sheets", [])) == 1


def ods_first_sheet_row_count(file_path: "str | Path") -> int:
    """Return the row count of the first sheet. 0 if no sheets.

    Spec: ODS table:table-row element (FACT-ODS-001)
    """
    doc = _ods_load(file_path)
    sheets = doc.get("sheets", [])
    if not sheets:
        return 0
    return sheets[0].get("row_count", 0)


def ods_all_sheets_named(file_path: "str | Path") -> bool:
    """Return True if every sheet has a non-empty, non-whitespace name.

    True vacuously when there are no sheets.

    Spec: ODS table:table element (FACT-ODS-001)
    """
    doc = _ods_load(file_path)
    sheets = doc.get("sheets", [])
    return all(sheet.get("name", "").strip() for sheet in sheets)


def ods_has_uniform_sheet_row_count(file_path: "str | Path") -> bool:
    """Return True if all sheets have the same row count. True if ≤1 sheet.

    Spec: ODS table:table-row element (FACT-ODS-001)
    """
    doc = _ods_load(file_path)
    sheets = doc.get("sheets", [])
    if len(sheets) <= 1:
        return True
    counts = {sheet.get("row_count", 0) for sheet in sheets}
    return len(counts) == 1


def ods_min_sheet_row_count(file_path: "str | Path") -> int:
    """Return the minimum row count across all sheets. 0 if no sheets.

    Spec: ODS table:table-row element (FACT-ODS-001)
    """
    doc = _ods_load(file_path)
    sheets = doc.get("sheets", [])
    if not sheets:
        return 0
    return min(sheet.get("row_count", 0) for sheet in sheets)
