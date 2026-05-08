#!/usr/bin/env python3
"""
fodt_parser.py — FODT (Flat OpenDocument Text) parser prototype.

Gate 4 prototype for the format-factory project.

IMPORTANT: This is a Gate 4 PROTOTYPE only.
- For exploration and format understanding.
- NOT product source code (which lives in src/python/fodt/ at Gate 10+).
- Covers only the ODF 1.3 structures needed to validate the 4 Gate 3 samples.
- Reuses ~40% of the FODS parser pattern (namespace handling, MAX_FILE_BYTES, error return).
- Python stdlib only. No third-party dependencies.

Usage:
    from fodt_parser import parse_fodt
    result = parse_fodt("path/to/document.fodt")

    result keys:
        mime_type    : str — office:mimetype attribute value
        version      : str — office:version attribute value
        paragraphs   : list[dict] — text:p and text:h elements (in document order)
        lists        : list[dict] — text:list elements
        tables       : list[dict] — table:table elements
        word_count   : int — total words across paragraphs and headings
        errors       : list[str] — non-fatal warnings/issues (empty = clean parse)

    On fatal error (XML parse failure, wrong root), returns:
        {"error": str, "errors": [str]}

License: Apache-2.0 (project-owned, format-factory)
Created: 2026-05-08 (run045)
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Namespace URIs
# ---------------------------------------------------------------------------
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text":   "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table":  "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "style":  "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo":     "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
}

# Clark-notation tag names
_TAG = {k: "{%s}%s" % (v, k) for k, v in NS.items()}

def _tag(ns: str, local: str) -> str:
    return "{%s}%s" % (NS[ns], local)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_FILE_BYTES = 100 * 1024 * 1024  # 100 MB

EXPECTED_ROOT_LOCAL = "document"
EXPECTED_MIME_TYPE  = "application/vnd.oasis.opendocument.text-flat-xml"

# ---------------------------------------------------------------------------
# List style detection helpers
# ---------------------------------------------------------------------------

def _collect_list_style_map(root: ET.Element) -> dict[str, str]:
    """
    Build a map from list-style name → "bullet" | "numbered" | "unknown".

    Scans office:automatic-styles for text:list-style elements.
    Each contains child text:list-level-style-bullet or text:list-level-style-number.
    """
    style_map: dict[str, str] = {}

    auto_styles = root.find(_tag("office", "automatic-styles"))
    if auto_styles is None:
        return style_map

    for ls in auto_styles.iter(_tag("text", "list-style")):
        name = ls.get(_tag("style", "name")) or ls.get("style:name") or ""
        if not name:
            # Try without namespace (plain attribute)
            name = ls.attrib.get("{urn:oasis:names:tc:opendocument:xmlns:style:1.0}name", "")
        if not name:
            continue

        has_bullet   = ls.find(_tag("text", "list-level-style-bullet")) is not None
        has_numbered = ls.find(_tag("text", "list-level-style-number")) is not None

        if has_bullet:
            style_map[name] = "bullet"
        elif has_numbered:
            style_map[name] = "numbered"
        else:
            style_map[name] = "unknown"

    return style_map


# ---------------------------------------------------------------------------
# Content extraction helpers
# ---------------------------------------------------------------------------

def _itertext_str(element: ET.Element) -> str:
    """Concatenate all text within an element (depth-first)."""
    return "".join(element.itertext())


def _extract_paragraphs_and_headings(office_text: ET.Element) -> list[dict]:
    """
    Extract text:p and text:h direct children of office:text.
    Returns list of dicts with element/text/style_name/outline_level.
    """
    results = []
    for child in office_text:
        tag = child.tag
        if tag == _tag("text", "p"):
            text = _itertext_str(child).strip()
            style_name = (
                child.get(_tag("text", "style-name"))
                or child.attrib.get("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name", "")
                or "Default"
            )
            results.append({
                "element": "paragraph",
                "text": text,
                "style_name": style_name,
                "outline_level": None,
            })
        elif tag == _tag("text", "h"):
            text = _itertext_str(child).strip()
            style_name = (
                child.get(_tag("text", "style-name"))
                or child.attrib.get("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name", "")
                or "Default"
            )
            level_str = (
                child.get(_tag("text", "outline-level"))
                or child.attrib.get("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}outline-level", "1")
            )
            try:
                outline_level = int(level_str)
            except (TypeError, ValueError):
                outline_level = 1
            results.append({
                "element": "heading",
                "text": text,
                "style_name": style_name,
                "outline_level": outline_level,
            })
    return results


def _extract_lists(office_text: ET.Element, list_style_map: dict[str, str]) -> list[dict]:
    """
    Extract text:list elements (direct children of office:text).
    """
    results = []
    for child in office_text:
        if child.tag != _tag("text", "list"):
            continue

        style_name = (
            child.get(_tag("text", "style-name"))
            or child.attrib.get("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name", "")
        )
        list_style = list_style_map.get(style_name, "unknown")

        items = []
        _collect_list_items(child, items, level=1)

        results.append({
            "element": "list",
            "list_style": list_style,
            "items": items,
        })
    return results


def _collect_list_items(
    list_elem: ET.Element,
    items: list[dict],
    level: int,
) -> None:
    """
    Recursively collect text:list-item entries.
    Each item contains text:p as its content (may have nested text:list).
    """
    for li in list_elem:
        if li.tag != _tag("text", "list-item"):
            continue
        # Extract text from text:p children
        item_text_parts = []
        nested_list = None
        for child in li:
            if child.tag == _tag("text", "p"):
                item_text_parts.append(_itertext_str(child).strip())
            elif child.tag == _tag("text", "list"):
                nested_list = child
        text = " ".join(t for t in item_text_parts if t)
        items.append({"text": text, "level": level})
        if nested_list is not None:
            _collect_list_items(nested_list, items, level + 1)


def _extract_tables(office_text: ET.Element) -> list[dict]:
    """
    Extract table:table elements (direct children of office:text).
    """
    results = []
    for child in office_text:
        if child.tag != _tag("table", "table"):
            continue

        name = (
            child.get(_tag("table", "name"))
            or child.attrib.get("{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name", "")
            or ""
        )
        rows = []
        for row in child:
            if row.tag != _tag("table", "table-row"):
                continue
            cells = []
            for cell in row:
                if cell.tag != _tag("table", "table-cell"):
                    continue
                # Extract text from all text:p children
                cell_text_parts = []
                for p in cell:
                    if p.tag == _tag("text", "p"):
                        cell_text_parts.append(_itertext_str(p).strip())
                cells.append(" ".join(cell_text_parts))
            if cells:
                rows.append(cells)

        results.append({
            "element": "table",
            "name": name,
            "rows": rows,
        })
    return results


# ---------------------------------------------------------------------------
# Word count
# ---------------------------------------------------------------------------

def _compute_word_count(paragraphs: list[dict]) -> int:
    """Count total words across all paragraph and heading elements."""
    count = 0
    for p in paragraphs:
        text = p.get("text", "")
        if text:
            count += len(text.split())
    return count


# ---------------------------------------------------------------------------
# Main parse function
# ---------------------------------------------------------------------------

def parse_fodt(filepath: str) -> dict[str, Any]:
    """
    Parse a FODT file and return a structured result.

    Returns a dict with keys:
        mime_type, version, paragraphs, lists, tables, word_count, errors

    On fatal error, returns:
        {"error": <str>, "errors": [<str>]}

    Never raises unhandled exceptions.
    """
    # ------------------------------------------------------------------
    # File size guard
    # ------------------------------------------------------------------
    try:
        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_BYTES:
            return {
                "error": f"File too large: {file_size} bytes > {MAX_FILE_BYTES} bytes limit",
                "errors": [f"file_too_large: {file_size} bytes"],
            }
    except OSError as e:
        return {
            "error": f"Cannot access file: {e}",
            "errors": [f"file_not_found: {e}"],
        }

    # ------------------------------------------------------------------
    # XML parse
    # ------------------------------------------------------------------
    try:
        tree = ET.parse(filepath)
    except ET.ParseError as e:
        return {
            "error": f"XML parse error: {e}",
            "errors": [f"parse_error: {e}"],
        }
    except RecursionError:
        return {
            "error": "XML structure caused recursion limit exceeded",
            "errors": ["recursion_limit_exceeded"],
        }

    root = tree.getroot()

    # ------------------------------------------------------------------
    # Root element check (FR-001)
    # ------------------------------------------------------------------
    expected_root_tag = _tag("office", EXPECTED_ROOT_LOCAL)
    if root.tag != expected_root_tag:
        return {
            "error": (
                f"Root element is not office:document "
                f"(got '{root.tag}')"
            ),
            "errors": ["wrong_root_element"],
        }

    # ------------------------------------------------------------------
    # MIME type check (FR-001)
    # ------------------------------------------------------------------
    mime_attr_key = _tag("office", "mimetype")
    mime_type = root.get(mime_attr_key, "")
    if not mime_type:
        mime_type = root.attrib.get(
            "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}mimetype", ""
        )

    errors: list[str] = []
    if mime_type != EXPECTED_MIME_TYPE:
        errors.append(
            f"Unexpected mimetype: '{mime_type}' "
            f"(expected '{EXPECTED_MIME_TYPE}')"
        )

    version_attr_key = _tag("office", "version")
    version = root.get(version_attr_key, "") or root.attrib.get(
        "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}version", ""
    )

    # ------------------------------------------------------------------
    # Collect list style map (FR-004)
    # ------------------------------------------------------------------
    list_style_map = _collect_list_style_map(root)

    # ------------------------------------------------------------------
    # Locate office:body/office:text
    # ------------------------------------------------------------------
    body = root.find(_tag("office", "body"))
    if body is None:
        return {
            "error": "office:body element not found",
            "errors": ["missing_body"],
        }

    office_text = body.find(_tag("office", "text"))
    if office_text is None:
        return {
            "error": "office:body/office:text element not found",
            "errors": ["missing_office_text"],
        }

    # ------------------------------------------------------------------
    # Extract content (FR-002, FR-003, FR-004, FR-005)
    # ------------------------------------------------------------------
    paragraphs = _extract_paragraphs_and_headings(office_text)
    lists      = _extract_lists(office_text, list_style_map)
    tables     = _extract_tables(office_text)

    # ------------------------------------------------------------------
    # Word count (FR-006)
    # ------------------------------------------------------------------
    word_count = _compute_word_count(paragraphs)

    return {
        "mime_type":  mime_type,
        "version":    version,
        "paragraphs": paragraphs,
        "lists":      lists,
        "tables":     tables,
        "word_count": word_count,
        "errors":     errors,
    }


# ---------------------------------------------------------------------------
# CLI (optional — for manual testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python fodt_parser.py <path.fodt>", file=sys.stderr)
        sys.exit(1)

    result = parse_fodt(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
