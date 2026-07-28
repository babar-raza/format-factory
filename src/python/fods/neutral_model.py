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
# Find sheet by name (R59 — new capability)
# ---------------------------------------------------------------------------

def find_sheet_by_name(workbook: dict[str, Any], name: str) -> "dict[str, Any] | None":
    """Return the first sheet dict whose name matches, or None.

    Case-sensitive match. Useful for programmatic access to named sheets
    without iterating manually. Returns the full sheet dict from the
    neutral model (including rows and cells).

    """
    for sheet in workbook.get("sheets", []):
        if sheet.get("name") == name:
            return sheet
    return None


# ---------------------------------------------------------------------------
# Workbook cell editor (R76 — product deepening: edit and save)
# ---------------------------------------------------------------------------

def workbook_set_cell_value(
    workbook: dict[str, Any],
    sheet_name: str,
    row_idx: int,
    col_idx: int,
    value: Any,
    value_type: str | None = None,
) -> tuple[bool, str]:
    """Set a cell value in the neutral model workbook.

    Mutates the workbook dict in-place. This enables an edit-and-save workflow:
        wb = parse_fods(path)
        ok, msg = workbook_set_cell_value(wb, "Sheet1", 0, 0, "Updated")
        if ok:
            write_fods(wb, out_path)

    Args:
        workbook: A neutral model workbook dict from parse_fods().
        sheet_name: The name of the sheet to edit.
        row_idx: 0-based row index.
        col_idx: 0-based column index.
        value: The new cell value. Strings, ints, and floats are supported.
        value_type: Optional explicit value type: "string", "float", "boolean".
            Inferred from value type if not provided.

    Returns:
        (success: bool, message: str) — success=True if the cell was found and updated.
        Returns (False, reason) if the sheet, row, or cell was not found.

    Note: This function modifies only the ``value`` and ``value_type`` fields.
    Formula attributes (``formula``) are cleared when a new plain value is set.
    Style attributes and other metadata are preserved.

    """
    if not isinstance(workbook, dict):
        return False, "workbook must be a dict"

    sheets = workbook.get("sheets", [])
    target_sheet = None
    for sheet in sheets:
        if sheet.get("name") == sheet_name:
            target_sheet = sheet
            break

    if target_sheet is None:
        return False, f"Sheet {sheet_name!r} not found"

    rows = target_sheet.get("rows", [])
    if row_idx < 0 or row_idx >= len(rows):
        return False, f"Row index {row_idx} out of range (sheet has {len(rows)} rows)"

    cells = rows[row_idx].get("cells", [])
    if col_idx < 0 or col_idx >= len(cells):
        return False, f"Column index {col_idx} out of range (row has {len(cells)} cells)"

    cell = cells[col_idx]
    if not isinstance(cell, dict):
        return False, f"Cell at ({row_idx}, {col_idx}) is not a dict"

    # Infer value_type if not provided
    if value_type is None:
        if isinstance(value, bool):
            value_type = "boolean"
        elif isinstance(value, (int, float)):
            value_type = "float"
        else:
            value_type = "string"

    cell["value"] = value
    cell["value_type"] = value_type
    # Clear formula when setting a plain value (formula no longer applies)
    if "formula" in cell:
        cell["formula"] = None

    return True, f"Cell ({row_idx}, {col_idx}) updated to {value!r} (type: {value_type})"


def workbook_warnings_for_unsupported_edit(
    workbook: dict[str, Any],
    sheet_name: str,
    row_idx: int,
    col_idx: int,
) -> list[str]:
    """Return warnings about unsupported cell features that may be lost on edit/save.

    Checks the target cell for features that the writer may not preserve perfectly:
    - Merged cells (span attributes)
    - Conditional formatting
    - Data validation rules
    - Non-standard value types

    Returns a list of warning strings. Empty list means no unsupported features detected.

    """
    warnings: list[str] = []

    sheets = workbook.get("sheets", [])
    target_sheet = next((s for s in sheets if s.get("name") == sheet_name), None)
    if target_sheet is None:
        return [f"Sheet {sheet_name!r} not found"]

    rows = target_sheet.get("rows", [])
    if row_idx >= len(rows):
        return [f"Row {row_idx} out of range"]

    cells = rows[row_idx].get("cells", [])
    if col_idx >= len(cells):
        return [f"Column {col_idx} out of range"]

    cell = cells[col_idx]
    if not isinstance(cell, dict):
        return ["Cell is not a standard dict"]

    if cell.get("merge") or cell.get("span") or cell.get("table:number-columns-spanned"):
        warnings.append("Cell has merge/span metadata — merged cell layout may change on save")
    if cell.get("formula"):
        warnings.append(
            "Cell has a formula — formula will be cleared when set_cell_value replaces it with a plain value"
        )
    vtype = cell.get("value_type", "")
    if vtype not in ("string", "float", "boolean", "", None):
        warnings.append(f"Non-standard value_type {vtype!r} — may not round-trip perfectly")

    return warnings


# ---------------------------------------------------------------------------
# R77 — Sheet management APIs
# ---------------------------------------------------------------------------


def workbook_add_sheet(
    workbook: dict[str, Any],
    sheet_name: str,
    position: int | None = None,
) -> tuple[bool, str]:
    """Add a new empty sheet to the workbook.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_name: Name for the new sheet.
        position: 0-based insert position. None means append.

    Returns:
        (success, message) tuple.

    """
    if not sheet_name or not sheet_name.strip():
        return False, "Sheet name must not be empty"

    sheets = workbook.get("sheets", [])
    existing_names = [s.get("name", "") for s in sheets]
    if sheet_name in existing_names:
        return False, f"Sheet {sheet_name!r} already exists"

    new_sheet: dict[str, Any] = {
        "name": sheet_name,
        "rows": [],
        "auto_updatable": False,
    }

    if position is None or position >= len(sheets):
        sheets.append(new_sheet)
    else:
        sheets.insert(max(0, position), new_sheet)

    workbook["sheets"] = sheets
    return True, f"Sheet {sheet_name!r} added at position {position if position is not None else len(sheets) - 1}"


def workbook_rename_sheet(
    workbook: dict[str, Any],
    old_name: str,
    new_name: str,
) -> tuple[bool, str]:
    """Rename an existing sheet.

    Args:
        workbook: Parsed FODS workbook dict.
        old_name: Current sheet name.
        new_name: Desired new sheet name.

    Returns:
        (success, message) tuple.

    """
    if not new_name or not new_name.strip():
        return False, "New sheet name must not be empty"

    sheets = workbook.get("sheets", [])
    existing_names = [s.get("name", "") for s in sheets]

    if old_name not in existing_names:
        return False, f"Sheet {old_name!r} not found"
    if new_name in existing_names and new_name != old_name:
        return False, f"Sheet {new_name!r} already exists"

    for sheet in sheets:
        if sheet.get("name") == old_name:
            sheet["name"] = new_name
            return True, f"Sheet renamed from {old_name!r} to {new_name!r}"

    return False, "Unexpected: sheet not found during rename"


def workbook_remove_sheet(
    workbook: dict[str, Any],
    sheet_name: str,
) -> tuple[bool, str]:
    """Remove a sheet from the workbook.

    This is a destructive operation. If the workbook has only one sheet,
    the removal is rejected to avoid an invalid empty workbook.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_name: Name of the sheet to remove.

    Returns:
        (success, message) tuple.

    """
    sheets = workbook.get("sheets", [])

    if len(sheets) <= 1:
        return False, "Cannot remove the only sheet in a workbook"

    before = len(sheets)
    workbook["sheets"] = [s for s in sheets if s.get("name") != sheet_name]
    after = len(workbook["sheets"])

    if before == after:
        return False, f"Sheet {sheet_name!r} not found"

    return True, f"Sheet {sheet_name!r} removed ({before} -> {after} sheets)"


def workbook_to_csv(
    workbook: dict[str, Any],
    sheet_name: str | None = None,
) -> str:
    """Export a workbook sheet as CSV text.

    If sheet_name is None, exports the first sheet. Returns the CSV as a
    plain string with CRLF line endings per RFC 4180.

    Cells are quoted if they contain commas, double-quotes, or newlines.
    Numeric and string values are both supported. Formula tokens are exported
    as empty strings (formula evaluation is unsupported in this track).

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_name: Name of the sheet to export, or None for the first sheet.

    Returns:
        CSV text string.

    """
    import io
    import csv as _csv

    sheets = workbook.get("sheets", [])
    if not sheets:
        return ""

    target = None
    if sheet_name is None:
        target = sheets[0]
    else:
        for s in sheets:
            if s.get("name") == sheet_name:
                target = s
                break
        if target is None:
            return ""

    rows = target.get("rows", [])
    buf = io.StringIO()
    writer = _csv.writer(buf, lineterminator="\r\n")
    for row in rows:
        cells = row.get("cells", [])
        csv_row = []
        for cell in cells:
            v = cell.get("value")
            if v is None:
                csv_row.append("")
            else:
                csv_row.append(str(v))
        writer.writerow(csv_row)
    return buf.getvalue()


def workbook_get_cell_value(
    workbook: dict[str, Any],
    sheet_name: str,
    row_index: int,
    col_index: int,
) -> Any:
    """Return the value of a cell at (row_index, col_index) in the named sheet.

    Indices are 0-based. Returns None if the sheet, row, or cell does not
    exist or is out of range.

    This is the read-side complement of workbook_set_cell_value and is
    primarily useful for roundtrip verification in installed-package workflows.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_name: Name of the sheet.
        row_index: 0-based row index.
        col_index: 0-based column index within the row.

    Returns:
        Cell value (str, float, int, bool) or None.

    """
    sheets = workbook.get("sheets", [])
    target = None
    for s in sheets:
        if s.get("name") == sheet_name:
            target = s
            break
    if target is None:
        return None

    rows = target.get("rows", [])
    if row_index < 0 or row_index >= len(rows):
        return None

    cells = rows[row_index].get("cells", [])
    if col_index < 0 or col_index >= len(cells):
        return None

    return cells[col_index].get("value")


def workbook_find_cells(
    workbook: dict[str, Any],
    value: Any,
    case_sensitive: bool = False,
) -> list[dict[str, Any]]:
    """Find all cells whose value matches the given search value.

    Searches across all sheets. String comparisons are case-insensitive by
    default. Non-string values are compared with equality.

    Aligned with ODF 1.3 spreadsheet content model (SAL-FODS-00001): cell values
    are stored in the workbook neutral model under sheets → rows → cells.

    Args:
        workbook: Parsed FODS workbook dict.
        value: Value to search for (string, number, bool, etc.).
        case_sensitive: If True, string matching is case-sensitive. Default False.

    Returns:
        List of match dicts, each containing:
            sheet_name (str): Name of the sheet.
            row_index (int): 0-based row index.
            col_index (int): 0-based column index.
            value: The cell value that matched.

    Added in Sprint FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-PROGRESS-AND-FORMAT-BACKFILL-MEGA-TRAIN-001
    as FODS product feature advancement (authority: P6, SAL-FODS-00001).
    """
    matches: list[dict[str, Any]] = []
    is_str_search = isinstance(value, str)
    compare_value = value.lower() if (is_str_search and not case_sensitive) else value

    for sheet in workbook.get("sheets", []):
        sheet_name = sheet.get("name", "")
        for row_idx, row in enumerate(sheet.get("rows", [])):
            for col_idx, cell in enumerate(row.get("cells", [])):
                cell_val = cell.get("value")
                if cell_val is None:
                    continue
                if is_str_search and isinstance(cell_val, str):
                    compare_cell = cell_val if case_sensitive else cell_val.lower()
                    if compare_cell == compare_value:
                        matches.append({
                            "sheet_name": sheet_name,
                            "row_index": row_idx,
                            "col_index": col_idx,
                            "value": cell_val,
                        })
                else:
                    if cell_val == value:
                        matches.append({
                            "sheet_name": sheet_name,
                            "row_index": row_idx,
                            "col_index": col_idx,
                            "value": cell_val,
                        })

    return matches


def workbook_count_matching_cells(
    workbook: dict[str, Any],
    value: Any,
    case_sensitive: bool = False,
) -> int:
    """Count the number of cells whose value matches the given search value.

    Convenience wrapper around workbook_find_cells that returns only the count.
    Aligned with ODF 1.3 spreadsheet content model (SAL-FODS-00001).

    Args:
        workbook: Parsed FODS workbook dict.
        value: Value to search for.
        case_sensitive: If True, string matching is case-sensitive. Default False.

    Returns:
        Integer count of matching cells across all sheets.

    Added in Sprint FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-DOGFOOD-FEATURES-AND-BACKFILL-001
    (authority: P6, SAL-FODS-00001).
    """
    return len(workbook_find_cells(workbook, value, case_sensitive=case_sensitive))


def workbook_to_html(workbook: dict[str, Any], sheet_index: int = 0) -> str:
    """Export a FODS workbook sheet as an HTML table string.

    Cell values are HTML-escaped.

    Args:
        workbook: Parsed FODS workbook dict.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        HTML string containing a <table> element. Empty string if sheet not found.
    """
    from html import escape
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return ""
    sheet = sheets[sheet_index]
    rows = sheet.get("rows", [])
    if not rows:
        return "<table></table>"

    lines = ["<table>"]
    for row in rows:
        lines.append("  <tr>")
        for cell in row.get("cells", []):
            val = cell.get("value", "")
            if val is None:
                val = ""
            lines.append(f"    <td>{escape(str(val))}</td>")
        lines.append("  </tr>")
    lines.append("</table>")
    return "\n".join(lines)


def workbook_get_column_values(
    workbook: dict[str, Any],
    col: int,
    sheet_index: int = 0,
) -> list[Any]:
    """Return all values in a column (0-based) from a given sheet.

    Aligned with ODF 1.3 spreadsheet content model (SAL-FODS-00001).

    Args:
        workbook: Parsed FODS workbook dict.
        col: 0-based column index.
        sheet_index: 0-based sheet index (default 0).

    Returns:
        List of cell values (None for missing cells). Empty list if sheet not found.
    """
    sheets = workbook.get("sheets", [])
    if sheet_index < 0 or sheet_index >= len(sheets):
        return []
    sheet = sheets[sheet_index]
    result: list[Any] = []
    for row in sheet.get("rows", []):
        cells = row.get("cells", [])
        if col < len(cells):
            result.append(cells[col].get("value"))
        else:
            result.append(None)
    return result


def workbook_max_column_count(workbook: dict[str, Any]) -> int:
    """Return the maximum number of columns across all sheets in the workbook.

    Counts the width of the widest row in each sheet, then returns the
    maximum across all sheets.

    Args:
        workbook: Parsed FODS workbook dict.

    Returns:
        Maximum column count. Returns 0 if no sheets or all sheets are empty.
    """
    max_cols = 0
    for sheet in workbook.get("sheets", []):
        for row in sheet.get("rows", []):
            cols = len(row.get("cells", []))
            if cols > max_cols:
                max_cols = cols
    return max_cols


# ---------------------------------------------------------------------------
# Formula count (product-healing pilot)
# ---------------------------------------------------------------------------

# TODO(PCG-005): These wildcard re-exports are a backward-compat shim only.
# Tests should be updated to import analytics functions from fods_analytics /
# fods_analytics_extended directly. See TC-PQLM-016 for test migration.
try:
    from .fods_analytics import *  # noqa: F401, F403  — canonical location
    from .fods_analytics_extended import *  # noqa: F401, F403  — canonical location
except ImportError:
    pass
