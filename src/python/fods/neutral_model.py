"""
neutral_model.py -- Neutral model builder and validator for format-factory-fods.

Builds and validates the 6-entity FODS neutral model output:
  Workbook -> Sheet -> Row -> Cell (-> Formula), Warning

Used by parser.py to assemble the final result and validate structure
before returning (IR-FODS-018).

Neutral model schema reference: schemas/neutral-model/fods/model.yaml
Gate 5 artifact: Gate 5 PASSED (Babar Raza, 2026-05-06, run035).

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""

from __future__ import annotations

from typing import Any

from .constants import FORMAT_ID, SPEC_VERSION


# ---------------------------------------------------------------------------
# Warning helper
# ---------------------------------------------------------------------------

def make_warning(code: str, message: str, source: str | None = None) -> dict[str, Any]:
    """Build a structured Warning dict matching the neutral model Warning entity."""
    w: dict[str, Any] = {"code": code, "message": message}
    if source is not None:
        w["source"] = source
    return w


# ---------------------------------------------------------------------------
# Workbook builder
# ---------------------------------------------------------------------------

def build_workbook(
    odf_version_attr: str,
    mimetype: str | None,
    sheets: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    unsupported_features: list[str],
    parse_errors: list[dict[str, Any]],
    auto_styles_elem: Any | None = None,
    styles_elem: Any | None = None,
) -> dict[str, Any]:
    """Assemble the Workbook-level result dict matching the neutral model.

    Fields conform to the Workbook entity in schemas/neutral-model/fods/model.yaml.
    Additional fields (unsupported_features, parse_errors) extend the neutral
    model for product parser transparency.

    R55 TC-0055: ``auto_styles_elem`` and ``styles_elem`` hold captured
    ``office:automatic-styles`` and ``office:styles`` ET element objects.
    The writer re-emits them verbatim for style round-trip preservation.
    These fields are not JSON-serializable and are prefixed with ``_``.
    """
    wb: dict[str, Any] = {
        "format_id": FORMAT_ID,
        "spec_version": SPEC_VERSION,
        "odf_version_attr": odf_version_attr,
        "mimetype": mimetype,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "warnings": warnings,
        "unsupported_features": sorted(unsupported_features),
        "parse_errors": parse_errors,
    }
    if auto_styles_elem is not None:
        wb["_auto_styles_elem"] = auto_styles_elem
    if styles_elem is not None:
        wb["_styles_elem"] = styles_elem
    return wb


# ---------------------------------------------------------------------------
# Workbook validator (IR-FODS-018)
# ---------------------------------------------------------------------------

def validate_workbook(result: dict[str, Any]) -> list[str]:
    """Validate a parse_fods() result against the neutral model structure.

    Returns a list of violation strings. Empty list means valid.
    Does NOT raise -- callers decide whether to treat violations as fatal.
    """
    violations: list[str] = []

    # Required top-level fields
    for field in ("format_id", "spec_version", "odf_version_attr", "sheet_count", "sheets", "warnings"):
        if field not in result:
            violations.append(f"Workbook missing required field: {field!r}")

    if result.get("format_id") != FORMAT_ID:
        violations.append(
            f"Workbook.format_id must be {FORMAT_ID!r}; got {result.get('format_id')!r}"
        )

    sheets = result.get("sheets")
    if not isinstance(sheets, list):
        violations.append("Workbook.sheets must be a list")
        return violations  # can't validate sheets further

    sheet_count = result.get("sheet_count")
    if sheet_count != len(sheets):
        violations.append(
            f"Workbook.sheet_count {sheet_count} != len(sheets) {len(sheets)}"
        )

    for i, sheet in enumerate(sheets):
        violations.extend(_validate_sheet(sheet, i))

    warnings = result.get("warnings")
    if not isinstance(warnings, list):
        violations.append("Workbook.warnings must be a list")

    return violations


def _validate_sheet(sheet: dict[str, Any], expected_index: int) -> list[str]:
    violations: list[str] = []
    prefix = f"Sheet[{expected_index}]"

    for field in ("name", "index", "row_count", "rows"):
        if field not in sheet:
            violations.append(f"{prefix} missing required field: {field!r}")

    if sheet.get("index") != expected_index:
        violations.append(
            f"{prefix}.index must be {expected_index}; got {sheet.get('index')!r}"
        )

    rows = sheet.get("rows")
    if not isinstance(rows, list):
        violations.append(f"{prefix}.rows must be a list")
        return violations

    row_count = sheet.get("row_count")
    if row_count != len(rows):
        violations.append(
            f"{prefix}.row_count {row_count} != len(rows) {len(rows)}"
        )

    for j, row in enumerate(rows):
        violations.extend(_validate_row(row, j, prefix))

    return violations


def _validate_row(row: dict[str, Any], expected_index: int, sheet_prefix: str) -> list[str]:
    violations: list[str] = []
    prefix = f"{sheet_prefix}.Row[{expected_index}]"

    for field in ("index", "cells"):
        if field not in row:
            violations.append(f"{prefix} missing required field: {field!r}")

    if row.get("index") != expected_index:
        violations.append(
            f"{prefix}.index must be {expected_index}; got {row.get('index')!r}"
        )

    cells = row.get("cells")
    if not isinstance(cells, list):
        violations.append(f"{prefix}.cells must be a list")

    return violations


# ---------------------------------------------------------------------------
# Workbook statistics (R57 — new capability)
# ---------------------------------------------------------------------------

def workbook_stats(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return cell-level statistics for a parsed FODS workbook.

    Returns a dict with:
      sheet_count: int
      total_rows: int
      total_cells: int     (all cells including empty)
      non_empty_cells: int  (cells where value is not None)
      formula_cells: int    (cells with a table:formula attribute)
      per_sheet: list[dict] (per-sheet breakdown)

    Added in R57 Train E as a new product capability.
    Useful for format triage and content assessment pipelines.
    """
    stats: dict[str, Any] = {
        "sheet_count": 0,
        "total_rows": 0,
        "total_cells": 0,
        "non_empty_cells": 0,
        "formula_cells": 0,
        "per_sheet": [],
    }
    sheets = workbook.get("sheets", [])
    stats["sheet_count"] = len(sheets)
    for sheet in sheets:
        rows = sheet.get("rows", [])
        total_cells = sum(len(row.get("cells", [])) for row in rows)
        non_empty = sum(
            1 for row in rows
            for cell in row.get("cells", [])
            if cell.get("value") is not None
        )
        formula = sum(
            1 for row in rows
            for cell in row.get("cells", [])
            if cell.get("formula") is not None
        )
        stats["total_rows"] += len(rows)
        stats["total_cells"] += total_cells
        stats["non_empty_cells"] += non_empty
        stats["formula_cells"] += formula
        stats["per_sheet"].append({
            "name": sheet.get("name", ""),
            "index": sheet.get("index", 0),
            "row_count": len(rows),
            "total_cells": total_cells,
            "non_empty_cells": non_empty,
            "formula_cells": formula,
        })
    return stats


# ---------------------------------------------------------------------------
# Workbook type distribution (R59 — new capability)
# ---------------------------------------------------------------------------

def workbook_type_distribution(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return a distribution of cell value_types across the workbook.

    Counts how many cells have each value_type (float, int, string, boolean,
    percentage, currency, date, time, and empty/None). Useful for schema
    inference and format triage pipelines.

    Returns a dict with:
      by_type: dict[str, int]  — count per value_type label (empty = no value)
      total_cells: int
      per_sheet: list[dict]   — per-sheet breakdown with same by_type structure

    Added in R59 Train G as a product deepening capability.
    """
    total_by_type: dict[str, int] = {}
    total_cells = 0
    per_sheet = []

    for sheet in workbook.get("sheets", []):
        sheet_by_type: dict[str, int] = {}
        for row in sheet.get("rows", []):
            for cell in row.get("cells", []):
                vtype = cell.get("value_type") or ("empty" if cell.get("value") is None else "unknown")
                total_by_type[vtype] = total_by_type.get(vtype, 0) + 1
                sheet_by_type[vtype] = sheet_by_type.get(vtype, 0) + 1
                total_cells += 1
        per_sheet.append({
            "name": sheet.get("name", ""),
            "index": sheet.get("index", 0),
            "by_type": sheet_by_type,
        })

    return {
        "by_type": total_by_type,
        "total_cells": total_cells,
        "per_sheet": per_sheet,
    }


# ---------------------------------------------------------------------------
# Find sheet by name (R59 — new capability)
# ---------------------------------------------------------------------------

def find_sheet_by_name(workbook: dict[str, Any], name: str) -> "dict[str, Any] | None":
    """Return the first sheet dict whose name matches, or None.

    Case-sensitive match. Useful for programmatic access to named sheets
    without iterating manually. Returns the full sheet dict from the
    neutral model (including rows and cells).

    Added in R59 Train G as a product deepening capability.
    """
    for sheet in workbook.get("sheets", []):
        if sheet.get("name") == name:
            return sheet
    return None


# ---------------------------------------------------------------------------
# Workbook sheet summary (R60 — new capability)
# ---------------------------------------------------------------------------

def workbook_sheet_summary(workbook: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a compact per-sheet summary of the workbook.

    Each entry in the returned list is a dict with:
      name: str
      index: int
      row_count: int
      cell_count: int       (total cells including empty)
      non_empty_count: int  (cells where value is not None)
      formula_count: int    (cells with a formula attribute)

    Useful for quick structural overview without iterating all data.
    Added in R60 Train G as a product deepening capability.
    """
    summary = []
    for sheet in workbook.get("sheets", []):
        rows = sheet.get("rows", [])
        cell_count = sum(len(row.get("cells", [])) for row in rows)
        non_empty = sum(
            1 for row in rows
            for cell in row.get("cells", [])
            if cell.get("value") is not None
        )
        formula = sum(
            1 for row in rows
            for cell in row.get("cells", [])
            if cell.get("formula") is not None
        )
        summary.append({
            "name": sheet.get("name", ""),
            "index": sheet.get("index", 0),
            "row_count": len(rows),
            "cell_count": cell_count,
            "non_empty_count": non_empty,
            "formula_count": formula,
        })
    return summary


# ---------------------------------------------------------------------------
# Workbook empty rows (R60 — new capability)
# ---------------------------------------------------------------------------

def workbook_empty_rows(workbook: dict[str, Any]) -> dict[str, Any]:
    """Return empty-row statistics for the workbook.

    A row is "empty" if all its cells have value == None (or it has no cells).

    Returns a dict with:
      total_empty_rows: int           (across all sheets)
      per_sheet: list[dict]           (per-sheet breakdown)
        Each entry: {name, index, empty_row_count, total_row_count}

    Useful for data quality assessment and sparse-data detection.
    Added in R60 Train G as a product deepening capability.
    """
    total_empty = 0
    per_sheet = []
    for sheet in workbook.get("sheets", []):
        rows = sheet.get("rows", [])
        empty = sum(
            1 for row in rows
            if all(cell.get("value") is None for cell in row.get("cells", []))
        )
        total_empty += empty
        per_sheet.append({
            "name": sheet.get("name", ""),
            "index": sheet.get("index", 0),
            "empty_row_count": empty,
            "total_row_count": len(rows),
        })
    return {
        "total_empty_rows": total_empty,
        "per_sheet": per_sheet,
    }
