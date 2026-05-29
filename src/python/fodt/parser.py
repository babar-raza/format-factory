"""
parser.py -- FODT streaming parser for format-factory-fodt.

Public API:
  parse_fodt(file_path)        -- never raises; returns error dict on failure
  parse_fodt_strict(file_path) -- raises FodtInputError/FodtSizeError/FodtParseError

Implements IR-FODT-001 through IR-FODT-015:
  - IR-FODT-003: iterative list traversal (list_traversal.collect_list_items)
  - IR-FODT-014: ET.iterparse streaming (depth-tracking state machine)

Streaming strategy: xml.etree.ElementTree.iterparse with depth_in_text counter.
Direct children of office:text are processed on their "end" event and then
cleared from memory, so only one block is held at a time.

License: Apache-2.0
Package: format-factory-fodt v0.1.0
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# IR-FODT-004: use defusedxml when available for XXE protection
try:
    import defusedxml.ElementTree as _ET  # type: ignore[import]
    from defusedxml.ElementTree import ParseError as _ParseError  # type: ignore[import]
except ImportError:
    import xml.etree.ElementTree as _ET  # type: ignore[assignment]
    from xml.etree.ElementTree import ParseError as _ParseError  # type: ignore[assignment]

from .constants import (
    ATTR_MIMETYPE,
    ATTR_OUTLINE_LEVEL,
    ATTR_STYLE_NAME,
    ATTR_TABLE_COL_SPAN,
    ATTR_TABLE_NAME,
    ATTR_TABLE_ROW_SPAN,
    ATTR_VERSION,
    ATTR_XLINK_HREF,
    EXPECTED_MIMETYPE,
    MAX_FILE_BYTES,
    NS_TEXT,
    QN_BODY,
    QN_DOCUMENT,
    QN_DRAW_FRAME,
    QN_DRAW_IMAGE,
    QN_LIST,
    QN_SCRIPTS,
    QN_TABLE,
    QN_TABLE_CELL,
    QN_TABLE_ROW,
    QN_TEXT,
    QN_TEXT_A,
    QN_TEXT_H,
    QN_TEXT_NOTE,
    QN_TEXT_P,
    QN_TEXT_SPAN,
    TEXT_FIELD_LOCAL_NAMES,
    WARN_MISSING_MIMETYPE,
    WARN_NOTE_ELEMENT,
    WARN_UNEXPECTED_MIMETYPE,
    WARN_UNSUPPORTED_ELEMENT,
)
from .exceptions import FodtInputError, FodtParseError, FodtSizeError
from .list_traversal import collect_list_items, _collect_text
from .neutral_model import build_document, make_warning, validate_document


def parse_fodt(file_path: "str | os.PathLike") -> "dict[str, Any]":
    """Parse a FODT file and return the neutral model dict.

    Never raises. Returns {"error": str, "parse_errors": list} on failure.

    Args:
        file_path: Path to the .fodt file.

    Returns:
        Neutral model dict conforming to schemas/neutral-model/fodt/model.yaml,
        or an error dict with keys 'error' and 'parse_errors'.
    """
    try:
        return parse_fodt_strict(file_path)
    except (FodtInputError, FodtSizeError, FodtParseError) as exc:
        parse_errors: list = []
        if hasattr(exc, "parse_errors"):
            parse_errors = exc.parse_errors  # type: ignore[attr-defined]
        return {"error": str(exc), "parse_errors": parse_errors}
    except Exception as exc:  # pylint: disable=broad-except
        return {"error": f"Unexpected error: {exc}", "parse_errors": []}


def parse_fodt_strict(file_path: "str | os.PathLike") -> "dict[str, Any]":
    """Parse a FODT file and return the neutral model dict.

    Raises:
        FodtInputError: File does not exist or is not a regular file.
        FodtSizeError:  File exceeds MAX_FILE_BYTES (100 MB).
        FodtParseError: Malformed XML or invalid FODT structure.

    Args:
        file_path: Path to the .fodt file.

    Returns:
        Neutral model dict conforming to schemas/neutral-model/fodt/model.yaml.
    """
    path = Path(file_path)

    # IR-FODT-013: validate file exists and is a regular file
    if not path.exists():
        raise FodtInputError(f"File not found: {path}")
    if not path.is_file():
        raise FodtInputError(f"Path is not a regular file: {path}")

    # IR-FODT-002: file size guard
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise FodtSizeError(
            f"File size {size} bytes exceeds maximum {MAX_FILE_BYTES} bytes (100 MB): {path}"
        )

    return _parse_streaming(path)


# ---------------------------------------------------------------------------
# Internal streaming parser
# ---------------------------------------------------------------------------

def _parse_streaming(path: Path) -> "dict[str, Any]":
    """Core iterparse-based streaming parser (IR-FODT-014)."""
    warnings: list = []
    parse_errors: list = []
    unsupported_features: set = set()

    odf_version_attr: str = ""
    mimetype = None
    blocks: list = []
    lists: list = []
    tables: list = []
    content: list = []  # document-order unified sequence (R55 TC-0060)

    root_seen = False
    in_body = False
    in_text = False
    depth_in_text = 0  # 0 = at office:text level, 1 = direct child, 2+ = nested

    try:
        context = _ET.iterparse(str(path), events=("start", "end"))

        for event, elem in context:
            tag = elem.tag

            if event == "start":
                if not root_seen:
                    # IR-FODT-001: root must be office:document
                    if tag != QN_DOCUMENT:
                        err = FodtParseError(
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

                elif tag == QN_SCRIPTS:
                    # IR-FODT-016 (FODS pattern): detect macros, never execute
                    unsupported_features.add("macros")

                elif tag == QN_BODY:
                    in_body = True

                elif in_body and tag == QN_TEXT:
                    in_text = True

                elif in_text:
                    depth_in_text += 1

            else:  # event == "end"
                if in_text:
                    if depth_in_text > 0:
                        depth_in_text -= 1
                        if depth_in_text == 0:
                            # Direct child of office:text just completed
                            _handle_text_child(
                                elem, tag, blocks, lists, tables, content,
                                warnings, unsupported_features,
                            )
                            elem.clear()
                    else:
                        # office:text itself just ended
                        in_text = False

                elif in_body and tag == QN_BODY:
                    in_body = False

    except FodtParseError:
        raise
    except _ParseError as exc:
        err = FodtParseError(f"Malformed XML in {path}: {exc}")
        err.parse_errors = [{"code": "MALFORMED_XML", "message": str(err)}]  # type: ignore[attr-defined]
        raise err from exc

    if not root_seen:
        err = FodtParseError(f"Empty or unreadable XML: {path}")
        err.parse_errors = [{"code": "EMPTY_XML", "message": str(err)}]  # type: ignore[attr-defined]
        raise err

    result = build_document(
        odf_version_attr=odf_version_attr,
        mimetype=mimetype,
        blocks=blocks,
        lists=lists,
        tables=tables,
        content=content,
        warnings=warnings,
        unsupported_features=list(unsupported_features),
        parse_errors=parse_errors,
    )

    # IR-FODT-015: validate neutral model before returning
    violations = validate_document(result)
    for v in violations:
        result["warnings"].append(make_warning("NEUTRAL_MODEL_VIOLATION", v))

    return result


# ---------------------------------------------------------------------------
# Run extraction for inline span preservation (R55 TC-0057)
# ---------------------------------------------------------------------------

def _collect_runs(elem: Any) -> "list[dict[str, Any]]":
    """Extract inline runs from a text:p or text:h element.

    Returns a list of run dicts, each with:
      - "text": str  -- run text content
      - "style": str | None  -- text:style-name attribute (None for unstyled runs)
      - "href": str | None  -- xlink:href for text:a hyperlink runs (R56 TC-0057)

    A "run" is either:
      1. A text:span child with optional style-name
      2. A text:a child with xlink:href (hyperlink) — R56 TC-0057 criterion 3
      3. A plain text segment at the element level (elem.text, or child.tail)

    This is an additive field — the existing "text" key (concatenated plain text)
    remains for backward compatibility. The "runs" field enables span-aware writers.

    R55 TC-0057 (spans), R56 TC-0057 criterion 3 (hyperlinks).
    """
    runs: list = []

    # Text before the first child
    if elem.text:
        text = elem.text
        if text:
            runs.append({"text": text, "style": None, "href": None})

    for child in elem:
        if child.tag == QN_TEXT_SPAN:
            # Gather all text inside the span (recursively)
            span_text = _collect_text(child)
            style = child.get(ATTR_STYLE_NAME)
            if span_text:
                runs.append({"text": span_text, "style": style or None, "href": None})
        elif child.tag == QN_TEXT_A:
            # Hyperlink: capture href and display text (R56 TC-0057 criterion 3)
            href = child.get(ATTR_XLINK_HREF) or ""
            link_text = _collect_text(child)
            if link_text or href:
                runs.append({"text": link_text, "style": None, "href": href or None})
        else:
            pass  # other inline elements ignored (text-fields etc.)
        # Text after each child (tail belongs to the parent, not the child)
        if child.tail:
            runs.append({"text": child.tail, "style": None, "href": None})

    return runs


# ---------------------------------------------------------------------------
# Direct-child-of-office:text dispatcher
# ---------------------------------------------------------------------------

def _handle_text_child(
    elem: Any,
    tag: str,
    blocks: list,
    lists: list,
    tables: list,
    content: list,
    warnings: list,
    unsupported_features: set,
) -> None:
    """Dispatch processing for a completed direct child of office:text."""
    if tag == QN_TEXT_P:
        # IR-FODT-005: paragraph
        text = _collect_text(elem).strip()
        runs = _collect_runs(elem)
        block = {"type": "paragraph", "text": text, "heading_level": None, "runs": runs}
        blocks.append(block)
        content.append({"kind": "block", "data": block})

    elif tag == QN_TEXT_H:
        # IR-FODT-005, IR-FODT-010: heading with outline level
        text = _collect_text(elem).strip()
        runs = _collect_runs(elem)
        level_str = elem.get(ATTR_OUTLINE_LEVEL, "1")
        try:
            heading_level = int(level_str)
        except (TypeError, ValueError):
            heading_level = 1
        heading_level = max(1, min(6, heading_level))
        block = {"type": "heading", "text": text, "heading_level": heading_level, "runs": runs}
        blocks.append(block)
        content.append({"kind": "block", "data": block})

    elif tag == QN_LIST:
        # IR-FODT-006: list with iterative traversal (IR-FODT-003)
        items = collect_list_items(elem)
        lst = {"items": items}
        lists.append(lst)
        content.append({"kind": "list", "data": lst})

    elif tag == QN_TABLE:
        # IR-FODT-007: table within text context
        table_dict = _extract_table(elem)
        tables.append(table_dict)
        content.append({"kind": "table", "data": table_dict})

    elif tag == QN_DRAW_FRAME or tag == QN_DRAW_IMAGE:
        # IR-FODT-008: embedded frame/image detection
        unsupported_features.add("embedded-frame")
        warnings.append(make_warning(
            WARN_UNSUPPORTED_ELEMENT,
            f"draw:frame or draw:image at top level of office:text: "
            "embedded objects not supported in Tier 0-2",
        ))

    elif tag == QN_TEXT_NOTE:
        # R73 Train D: footnote/endnote detection (text:note element)
        # note-class attribute is "footnote" or "endnote" per ODF 1.3
        note_class = elem.get(f"{{{NS_TEXT}}}note-class", "note")
        unsupported_features.add("footnote-endnote")
        warnings.append(make_warning(
            WARN_NOTE_ELEMENT,
            f"text:note ({note_class}) detected: footnotes/endnotes are captured "
            "as unsupported_features but note body is not preserved in neutral model",
        ))

    else:
        # IR-FODT-009: text field detection (text:date, text:time, etc.)
        local = _get_local_name(tag)
        if local in TEXT_FIELD_LOCAL_NAMES and tag.startswith(f"{{{NS_TEXT}}}"):
            unsupported_features.add("text-field")


# ---------------------------------------------------------------------------
# Table extraction helper
# ---------------------------------------------------------------------------

def _extract_table(table_elem: Any) -> "dict[str, Any]":
    """Extract a table:table element into the neutral model Table dict."""
    name = table_elem.get(ATTR_TABLE_NAME) or ""
    rows: list = []

    for child in table_elem:
        if child.tag != QN_TABLE_ROW:
            continue
        cells: list = []
        for cell_elem in child:
            if cell_elem.tag != QN_TABLE_CELL:
                continue
            # Collect all text:p children for cell text (IR-FODT-011)
            cell_text_parts: list[str] = []
            for p in cell_elem:
                if p.tag == QN_TEXT_P:
                    cell_text_parts.append(_collect_text(p).strip())
            cell_dict: "dict[str, Any]" = {"text": " ".join(cell_text_parts)}
            # R73 Train D: table cell span preservation (ODF 1.3 section 9.1.4)
            col_span = _safe_int_fodt(cell_elem.get(ATTR_TABLE_COL_SPAN, "1"), 1)
            row_span = _safe_int_fodt(cell_elem.get(ATTR_TABLE_ROW_SPAN, "1"), 1)
            if col_span > 1:
                cell_dict["col_span"] = col_span
            if row_span > 1:
                cell_dict["row_span"] = row_span
            cells.append(cell_dict)
        if cells:
            rows.append({"cells": cells})

    return {"name": name or None, "rows": rows}


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _get_local_name(clark_tag: str) -> str:
    """Extract local name from Clark notation {uri}local."""
    if "}" in clark_tag:
        return clark_tag.split("}", 1)[1]
    return clark_tag


def _safe_int_fodt(value: "str | None", default: int) -> int:
    """Safely parse an integer attribute value, returning default on failure."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
