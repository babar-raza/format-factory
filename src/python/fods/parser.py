"""
parser.py -- FODS streaming parser for format-factory-fods.

Public API:
  parse_fods(file_path)        -- never raises; returns error dict on failure
  parse_fods_strict(file_path) -- raises FodsInputError/FodsSizeError/FodsParseError

Implements IR-FODS-001 through IR-FODS-020 (IR-FODS-008 formula eval deferred).

Streaming strategy: xml.etree.ElementTree.iterparse with elem.clear() after
each completed row/table to avoid holding the full DOM in memory (IR-FODS-002).

License: Apache-2.0
Package: format-factory-fods v0.1.0
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# IR-FODS-004: use defusedxml when available for XXE protection
try:
    import defusedxml.ElementTree as _ET  # type: ignore[import]
    from defusedxml.ElementTree import ParseError as _ParseError  # type: ignore[import]
except ImportError:
    import xml.etree.ElementTree as _ET  # type: ignore[assignment]
    from xml.etree.ElementTree import ParseError as _ParseError  # type: ignore[assignment]

from .constants import (
    ATTR_BOOL_VALUE,
    ATTR_COL_REPEAT,
    ATTR_COL_SPAN,
    ATTR_DATE_VALUE,
    ATTR_FORMULA,
    ATTR_MIMETYPE,
    ATTR_ROW_REPEAT,
    ATTR_ROW_SPAN,
    ATTR_STRING_VALUE,
    ATTR_TIME_VALUE,
    ATTR_VALUE,
    ATTR_VALUE_TYPE,
    ATTR_VERSION,
    ATTR_TABLE_NAME,
    EXPECTED_MIMETYPE,
    MAX_EXPAND_REPEAT,
    MAX_FILE_BYTES,
    QN_AUTO_STYLES,
    QN_CELL,
    QN_COVERED,
    QN_DOCUMENT,
    QN_DRAW_FRAME,
    QN_ROW,
    QN_SCRIPTS,
    QN_SPREADSHEET,
    QN_STYLES,
    QN_TABLE,
    QN_TABLE_COL,
    QN_TEXT_P,
    QN_TEXT_SPAN,
    WARN_COVERED_CELL,
    WARN_FORMULA_CELL,
    WARN_LARGE_REPEAT,
    WARN_MISSING_MIMETYPE,
    WARN_UNEXPECTED_MIMETYPE,
    WARN_UNSUPPORTED_ELEMENT,
    WARN_UNSUPPORTED_VALUE_TYPE,
)
from .exceptions import FodsInputError, FodsParseError, FodsSizeError
from .neutral_model import build_workbook, make_warning, validate_workbook


def parse_fods(file_path: "str | os.PathLike") -> "dict[str, Any]":
    """Parse a FODS file and return the neutral model dict.

    .. deprecated::
        This dict-based API is the legacy interface. Prefer the class-based API::

            from fods import FodsDocument
            doc = FodsDocument.from_file(file_path)

        parse_fods() remains supported for backward compatibility.

    Never raises. Returns {"error": str, "parse_errors": list} on failure.

    Args:
        file_path: Path to the .fods file.

    Returns:
        Neutral model dict conforming to schemas/neutral-model/fods/model.yaml,
        or an error dict with keys 'error' and 'parse_errors'.
    """
    try:
        return parse_fods_strict(file_path)
    except (FodsInputError, FodsSizeError, FodsParseError) as exc:
        parse_errors: list = []
        if hasattr(exc, "parse_errors"):
            parse_errors = exc.parse_errors  # type: ignore[attr-defined]
        return {"error": str(exc), "parse_errors": parse_errors}
    except Exception as exc:  # pylint: disable=broad-except
        return {"error": f"Unexpected error: {exc}", "parse_errors": []}


def parse_fods_strict(file_path: "str | os.PathLike") -> "dict[str, Any]":
    """Parse a FODS file and return the neutral model dict.

    Raises:
        FodsInputError: File does not exist or is not a regular file.
        FodsSizeError:  File exceeds MAX_FILE_BYTES (100 MB).
        FodsParseError: Malformed XML or invalid FODS structure.

    Args:
        file_path: Path to the .fods file.

    Returns:
        Neutral model dict conforming to schemas/neutral-model/fods/model.yaml.
    """
    path = Path(file_path)

    # IR-FODS-020: validate file exists and is a regular file
    if not path.exists():
        raise FodsInputError(f"File not found: {path}")
    if not path.is_file():
        raise FodsInputError(f"Path is not a regular file: {path}")

    # IR-FODS-003: file size guard
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise FodsSizeError(
            f"File size {size} bytes exceeds maximum {MAX_FILE_BYTES} bytes (100 MB): {path}"
        )

    return _parse_streaming(path)


# ---------------------------------------------------------------------------
# Internal streaming parser
# ---------------------------------------------------------------------------

def _parse_streaming(path: Path) -> "dict[str, Any]":
    """Core iterparse-based streaming parser (IR-FODS-002)."""
    warnings: list = []
    parse_errors: list = []
    unsupported_features: set = set()

    odf_version_attr: str = ""
    mimetype = None
    sheets: list = []
    # TC-0055: style metadata capture (element references, not cleared)
    auto_styles_elem = None
    styles_elem = None

    root_seen = False
    in_spreadsheet = False
    current_sheet = None
    sheet_index = 0

    try:
        context = _ET.iterparse(str(path), events=("start", "end"))

        for event, elem in context:
            tag = elem.tag

            if event == "start":
                if not root_seen:
                    # IR-FODS-001: root must be office:document
                    if tag != QN_DOCUMENT:
                        err = FodsParseError(
                            f"Root element must be office:document; got {tag!r}"
                        )
                        err.parse_errors = [{"code": "WRONG_ROOT", "message": str(err)}]  # type: ignore[attr-defined]
                        raise err
                    root_seen = True
                    odf_version_attr = elem.get(ATTR_VERSION, "")
                    raw_mime = elem.get(ATTR_MIMETYPE)
                    if raw_mime is None:
                        warnings.append(make_warning(
                            WARN_MISSING_MIMETYPE,
                            "office:mimetype attribute absent on office:document",
                        ))
                    elif raw_mime != EXPECTED_MIMETYPE:
                        warnings.append(make_warning(
                            WARN_UNEXPECTED_MIMETYPE,
                            f"office:mimetype is {raw_mime!r}; expected {EXPECTED_MIMETYPE!r}",
                        ))
                    mimetype = raw_mime

                elif tag == QN_SPREADSHEET:
                    in_spreadsheet = True

                elif tag == QN_SCRIPTS:
                    # IR-FODS-016: detect macros, never execute
                    unsupported_features.add("macros")

                elif tag == QN_TABLE and in_spreadsheet:
                    # Start a new sheet
                    current_sheet = {
                        "name": elem.get(ATTR_TABLE_NAME, f"Sheet{sheet_index + 1}"),
                        "index": sheet_index,
                        "row_count": 0,
                        "rows": [],
                    }

            else:  # event == "end"
                # TC-0055: capture styles sections verbatim before spreadsheet
                if tag == QN_AUTO_STYLES:
                    auto_styles_elem = elem
                elif tag == QN_STYLES:
                    styles_elem = elem

                # TC-0056: capture column definitions per sheet
                elif tag == QN_TABLE_COL and current_sheet is not None:
                    col_def = dict(elem.attrib)
                    current_sheet.setdefault("column_defs", []).append(col_def)

                elif tag == QN_ROW and current_sheet is not None:
                    # Process completed row
                    row_repeat = _safe_int(elem.get(ATTR_ROW_REPEAT, "1"), 1)
                    if row_repeat > MAX_EXPAND_REPEAT:
                        warnings.append(make_warning(
                            WARN_LARGE_REPEAT,
                            f"table:number-rows-repeated={row_repeat} exceeds cap "
                            f"{MAX_EXPAND_REPEAT}; capped",
                        ))
                        row_repeat = MAX_EXPAND_REPEAT

                    row_idx_base = len(current_sheet["rows"])
                    for rep in range(row_repeat):
                        row_dict = _process_row_elem(
                            elem,
                            row_idx_base + rep,
                            warnings,
                            unsupported_features,
                        )
                        current_sheet["rows"].append(row_dict)

                    elem.clear()

                elif tag == QN_TABLE and current_sheet is not None:
                    # Finalize sheet
                    current_sheet["row_count"] = len(current_sheet["rows"])
                    sheets.append(current_sheet)
                    current_sheet = None
                    sheet_index += 1
                    elem.clear()

                elif tag == QN_SPREADSHEET:
                    in_spreadsheet = False

    except FodsParseError:
        raise
    except _ParseError as exc:
        err = FodsParseError(f"Malformed XML in {path}: {exc}")
        err.parse_errors = [{"code": "MALFORMED_XML", "message": str(err)}]  # type: ignore[attr-defined]
        raise err from exc

    if not root_seen:
        err = FodsParseError(f"Empty or unreadable XML: {path}")
        err.parse_errors = [{"code": "EMPTY_XML", "message": str(err)}]  # type: ignore[attr-defined]
        raise err

    result = build_workbook(
        odf_version_attr=odf_version_attr,
        mimetype=mimetype,
        sheets=sheets,
        warnings=warnings,
        unsupported_features=list(unsupported_features),
        parse_errors=parse_errors,
        auto_styles_elem=auto_styles_elem,
        styles_elem=styles_elem,
    )

    # IR-FODS-018: validate neutral model before returning
    violations = validate_workbook(result)
    for v in violations:
        result["warnings"].append(make_warning("NEUTRAL_MODEL_VIOLATION", v))

    return result


# ---------------------------------------------------------------------------
# Row / cell helpers
# ---------------------------------------------------------------------------

def _process_row_elem(
    row_elem: Any,
    row_idx: int,
    warnings: list,
    unsupported_features: set,
) -> "dict[str, Any]":
    """Build a Row dict from a completed table:table-row element."""
    cells: list = []
    col_idx = 0

    for child in row_elem:
        tag = child.tag

        if tag == QN_DRAW_FRAME:
            # IR-FODS-015: chart/image detection (draw:frame as direct row child)
            unsupported_features.add("chart")
            warnings.append(make_warning(
                WARN_UNSUPPORTED_ELEMENT,
                f"draw:frame in row {row_idx} col {col_idx}: "
                "embedded objects not supported",
            ))
            col_idx += 1
            continue

        if tag not in (QN_CELL, QN_COVERED):
            continue

        is_covered = tag == QN_COVERED

        # IR-FODS-015: also detect draw:frame nested inside a cell
        for cell_child in child:
            if cell_child.tag == QN_DRAW_FRAME:
                unsupported_features.add("chart")
                warnings.append(make_warning(
                    WARN_UNSUPPORTED_ELEMENT,
                    f"draw:frame in row {row_idx} col {col_idx}: "
                    "embedded objects not supported",
                ))
                break

        # Column repeat (IR-FODS-011)
        col_repeat = _safe_int(child.get(ATTR_COL_REPEAT, "1"), 1)
        if col_repeat > MAX_EXPAND_REPEAT:
            warnings.append(make_warning(
                WARN_LARGE_REPEAT,
                f"table:number-columns-repeated={col_repeat} exceeds cap "
                f"{MAX_EXPAND_REPEAT}; capped",
            ))
            col_repeat = MAX_EXPAND_REPEAT

        # IR-FODS-009: covered cell warning
        if is_covered and col_repeat > 0:
            warnings.append(make_warning(
                WARN_COVERED_CELL,
                f"Covered cell at row {row_idx} col {col_idx}",
            ))

        value_type = child.get(ATTR_VALUE_TYPE)
        formula = child.get(ATTR_FORMULA)  # IR-FODS-008: capture, don't eval

 # R73 : merged-cell span metadata preservation (ODF 1.3 section 9.1.4)
        # table:number-columns-spanned / table:number-rows-spanned
        # Default 1 per ODF spec. Only non-trivial spans (>1) are reported.
        col_span = _safe_int(child.get(ATTR_COL_SPAN, "1"), 1)
        row_span = _safe_int(child.get(ATTR_ROW_SPAN, "1"), 1)

 # R73 : emit WARN_FORMULA_CELL when formula present (IR-FODS-008 transparency)
        if formula is not None:
            unsupported_features.add("formula")
            warnings.append(make_warning(
                WARN_FORMULA_CELL,
                f"Formula at row {row_idx} col {col_idx}: "
                "formula expression captured but not evaluated (IR-FODS-008)",
                source=f"row={row_idx},col={col_idx}",
            ))

        value = _extract_value(child, value_type, warnings, row_idx, col_idx)

        for rep in range(col_repeat):
            cell: "dict[str, Any]" = {
                "index": col_idx,
                "value_type": value_type,
                "value": value,
                "formula": formula,
                "is_covered": is_covered,
            }
            # Only add span fields when non-trivial (>1) to keep output compact
            if col_span > 1:
                cell["col_span"] = col_span
            if row_span > 1:
                cell["row_span"] = row_span
            cells.append(cell)
            col_idx += 1

    return {"index": row_idx, "cells": cells}


def _extract_value(
    cell_elem: Any,
    value_type: "str | None",
    warnings: list,
    row_idx: int,
    col_idx: int,
) -> Any:
    """Dispatch cell value extraction based on value-type (IR-FODS-007)."""
    if value_type is None:
        return None

    if value_type == "string":
        return _extract_string_value(cell_elem, value_type)

    if value_type in ("float", "percentage", "currency"):
        raw = cell_elem.get(ATTR_VALUE)
        if raw is not None:
            try:
                return float(raw)
            except ValueError:
                pass
        return _extract_text(cell_elem) or None

    if value_type == "boolean":
        # IR-FODS-014: normalise "true"/"1" -> True, "false"/"0" -> False
        raw = cell_elem.get(ATTR_BOOL_VALUE, "").strip().lower()
        if raw in ("true", "1"):
            return True
        if raw in ("false", "0"):
            return False
        return None

    if value_type == "date":
        return cell_elem.get(ATTR_DATE_VALUE)

    if value_type == "time":
        return cell_elem.get(ATTR_TIME_VALUE)

    if value_type == "void":
        return None

    # Unknown value type
    warnings.append(make_warning(
        WARN_UNSUPPORTED_VALUE_TYPE,
        f"Unsupported office:value-type {value_type!r} at row {row_idx} col {col_idx}",
    ))
    return _extract_text(cell_elem) or None


def _extract_string_value(cell_elem: Any, value_type: str) -> "str | None":
    """Extract string value: office:string-value first, then text content (IR-FODS-012/013)."""
    sv = cell_elem.get(ATTR_STRING_VALUE)
    if sv is not None:
        return sv
    return _extract_text(cell_elem)


def _extract_text(cell_elem: Any) -> "str | None":
    """Collect text from text:p children, strip whitespace (IR-FODS-019)."""
    parts: list = []
    for child in cell_elem:
        if child.tag == QN_TEXT_P:
            text = _collect_text(child)
            parts.append(text)
    result = " ".join(parts).strip()
    return result if result else None


def _collect_text(elem: Any) -> str:
    """Recursively collect text content from an element and its children."""
    parts: list = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        if child.tag == QN_TEXT_SPAN:
            parts.append(_collect_text(child))
        elif child.text:
            parts.append(child.text)
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _safe_int(value: str, default: int) -> int:
    """Parse int safely, returning default on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
