"""
writer.py -- FODT serializer for format-factory-fodt.

Writes a neutral model document dict to a FODT (Flat OpenDocument Text) XML file.

Public API:
  write_fodt(document, file_path)  -- serialize document to FODT file
  document_to_xml(document)        -- serialize document to XML string

R46 MT6: Two-product capability deepening. Adds write/export path to FOSS package.

R49 MT4/5: Object-model schema unification repair.
  - Parser emits ``blocks`` key with [{type, text, heading_level}] items.
  - Writer previously read ``paragraphs`` key only — produced empty XML for parser output.
  - Fix: accept ``blocks`` as canonical; ``paragraphs`` accepted as legacy alias.
  - Heading blocks (type='heading') serialized as ``text:h`` with ``text:outline-level``.
  - Paragraph blocks (type='paragraph') serialized as ``text:p``.
  - Legacy ``paragraphs`` list items serialized as ``text:p`` (backward compatible).

R54 MT6 (TC-0059/TC-0058 partial advance):
  - List blocks from ``document["lists"]`` serialized as ``text:list``/``text:list-item``.
  - Table blocks from ``document["tables"]`` serialized as ``table:table``, ``table:table-row``,
    ``table:table-cell`` with ``text:p`` cell content.

R55 TC-0057 (inline span preservation):
  - ``_write_span()`` helper emits ``text:span`` with ``text:style-name`` attribute.
  - ``_write_block()`` now checks for ``runs`` field: if present and non-empty, emits
    text:span wrappers for styled runs and plain text nodes for unstyled runs.
    Falls back to plain ``el.text = text`` when no runs are recorded.

R55 TC-0060 (document ordering):
  - ``document_to_xml()`` now checks for ``content`` key (R55 parser output).
  - When present, elements are emitted in document order using the ``content`` sequence.
  - Falls back to the old blocks → lists → tables sequence for backward compatibility.

Capability level: alpha-foss-preview (write subset — paragraphs, headings, lists (basic),
tables (basic), inline spans with style preservation (R55)).

License: Apache-2.0
Package: format-factory-fodt v0.1.0
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .exceptions import FodtInputError

# ODF 1.3 namespace URIs
_NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}

_MIMETYPE = "application/vnd.oasis.opendocument.text-flat-xml"

# Register namespaces so ET uses the short prefixes
for _prefix, _uri in _NS.items():
    ET.register_namespace(_prefix, _uri)


def _qn(ns_prefix: str, local: str) -> str:
    return f"{{{_NS[ns_prefix]}}}{local}"


def _write_span(parent: ET.Element, run: "dict[str, Any]") -> None:
    """Append a text:span, text:a, or plain text node for one run dict.

    If run["href"] is non-None, wraps the run text in a ``text:a`` element
    with ``xlink:href`` and ``xlink:type="simple"`` attributes (R56 TC-0057 criterion 3).
    If run["style"] is non-None, wraps the run text in a ``text:span`` element
    with a ``text:style-name`` attribute.
    Otherwise appends the text as a tail on the last child or as ``parent.text``.

    R55 TC-0057 (spans), R56 TC-0057 criterion 3 (hyperlinks).
    """
    run_text = str(run.get("text", "")) if run.get("text") is not None else ""
    style = run.get("style")
    href = run.get("href")

    if href:
        a_el = ET.SubElement(parent, _qn("text", "a"))
        a_el.set(_qn("xlink", "type"), "simple")
        a_el.set(_qn("xlink", "href"), href)
        a_el.text = run_text
    elif style:
        span_el = ET.SubElement(parent, _qn("text", "span"))
        span_el.set(_qn("text", "style-name"), style)
        span_el.text = run_text
    else:
        # Plain text — attach as tail of last child, or as parent.text
        children = list(parent)
        if children:
            last_child = children[-1]
            last_child.tail = (last_child.tail or "") + run_text
        else:
            parent.text = (parent.text or "") + run_text


def _write_block(parent: ET.Element, block: dict[str, Any]) -> None:
    """Append a text:p or text:h element for the given neutral model block.

    Handles canonical ``blocks`` items (from parser output):
      - type='paragraph' → text:p
      - type='heading'   → text:h with text:outline-level attribute

    Also handles legacy ``paragraphs`` list items (text_content/content keys).

    R49: replaces _write_paragraph to support heading blocks from parser output.
    R55 TC-0057: if block has non-empty ``runs`` list, emit text:span for styled runs.
    """
    block_type = block.get("type", "paragraph")
    text = block.get("text", block.get("text_content", block.get("content", "")))
    text = str(text) if text is not None else ""
    runs = block.get("runs")

    if block_type == "heading":
        el = ET.SubElement(parent, _qn("text", "h"))
        level = block.get("heading_level") or 1
        el.set(_qn("text", "outline-level"), str(level))
    else:
        # paragraph (default)
        el = ET.SubElement(parent, _qn("text", "p"))

    # If runs are available and at least one run has a style or href, emit spans/links
    if runs and any(r.get("style") or r.get("href") for r in runs):
        for run in runs:
            _write_span(el, run)
    else:
        el.text = text


def _write_list(parent: ET.Element, lst: dict[str, Any]) -> None:
    """Append a text:list element for the given neutral model List dict.

    R54 TC-0059 (partial): emits text:list with text:list-item children.
    R56 TC-0059 criterion 2: nested list hierarchy (level > 1) is now emitted
    correctly as nested text:list elements inside text:list-item.

    Each item in lst["items"] has "text" and "level" keys (1-based level).
    Items are assumed to be in document order. A level increase means nesting
    deeper inside the most recent list-item; a level decrease means returning
    to a parent list element.

    Algorithm: maintain a stack of open list elements indexed by level.
    When the item level equals the current level, append to current list.
    When the item level increases, open a new nested list inside the last item.
    When the item level decreases, pop back to the correct parent level.
    """
    items = lst.get("items", [])
    if not items:
        ET.SubElement(parent, _qn("text", "list"))
        return

    # Stack: list of (level, list_element) pairs.
    # The "list_el" on the stack is the text:list element we're currently appending to.
    root_list_el = ET.SubElement(parent, _qn("text", "list"))
    level_stack: list[tuple[int, ET.Element]] = [(1, root_list_el)]

    for item in items:
        item_level = item.get("level", 1)
        item_text = str(item.get("text", "")) if item.get("text") is not None else ""

        # Determine current top-of-stack level
        current_level, current_list_el = level_stack[-1]

        if item_level > current_level:
            # Need to nest deeper: create a new text:list inside the last list-item
            # The last item_el in current_list_el is where we nest
            last_items = [ch for ch in current_list_el if ch.tag == _qn("text", "list-item")]
            if last_items:
                # Nest inside the last existing list-item
                nesting_item_el = last_items[-1]
            else:
                # No existing item — create an empty item to nest under
                nesting_item_el = ET.SubElement(current_list_el, _qn("text", "list-item"))
            new_list_el = ET.SubElement(nesting_item_el, _qn("text", "list"))
            level_stack.append((item_level, new_list_el))
            current_list_el = new_list_el

        elif item_level < current_level:
            # Pop back to the appropriate parent level
            while len(level_stack) > 1 and level_stack[-1][0] > item_level:
                level_stack.pop()
            _, current_list_el = level_stack[-1]

        # Append item to current list
        item_el = ET.SubElement(current_list_el, _qn("text", "list-item"))
        p_el = ET.SubElement(item_el, _qn("text", "p"))
        p_el.text = item_text


def _write_table(parent: ET.Element, table: dict[str, Any]) -> None:
    """Append a table:table element for the given neutral model Table dict.

    R54 TC-0058 (partial): emits table:table with table:table-row and
    table:table-cell children. Each cell contains a text:p with cell text.

    Known limitation: cell styles, column widths, and other table attributes
    are not preserved (neutral model only stores text content). Full table
    round-trip requires neutral model extension (R55+).

    The ordering of tables relative to blocks and lists is not preserved.
    Tables are emitted after all lists.
    """
    name = table.get("name") or ""
    table_el = ET.SubElement(parent, _qn("table", "table"))
    if name:
        table_el.set(_qn("table", "name"), name)
    for row in table.get("rows", []):
        row_el = ET.SubElement(table_el, _qn("table", "table-row"))
        for cell in row.get("cells", []):
            cell_el = ET.SubElement(row_el, _qn("table", "table-cell"))
            p_el = ET.SubElement(cell_el, _qn("text", "p"))
            p_el.text = str(cell.get("text", "")) if cell.get("text") is not None else ""


def document_to_xml(document: dict[str, Any]) -> str:
    """Serialize a neutral model document dict to a FODT XML string.

    Accepts both canonical ``blocks`` key (parser output) and legacy
    ``paragraphs`` key. If ``blocks`` is present it takes precedence.

    Args:
        document: dict following the fodt neutral model schema.
                  Canonical key: ``blocks`` (list of block dicts with ``type``/``text``).
                  Legacy key: ``paragraphs`` (list of paragraph dicts with ``text_content``).
                  R54 keys: ``lists`` (list of List dicts), ``tables`` (list of Table dicts).
                  Optional keys: odf_version_attr.

    Returns:
        UTF-8 XML string (str) representing a valid FODT document.

    Note (R54): lists are emitted after all blocks; tables after all lists. Document ordering
    between blocks, lists, and tables is not preserved due to the neutral model's separate
    sequences. Full ordering requires a parser refactor (R55+).
    """
    if not isinstance(document, dict):
        raise FodtInputError("document must be a dict")

    # Accept blocks (canonical — matches parser output) or paragraphs (legacy alias)
    blocks = document.get("blocks")
    if blocks is None:
        blocks = document.get("paragraphs", [])
    if not isinstance(blocks, list):
        raise FodtInputError("document['blocks'] (or 'paragraphs') must be a list")

    lists = document.get("lists", [])
    tables = document.get("tables", [])

    version = document.get("odf_version_attr", "1.3")

    # Build root element
    doc_el = ET.Element(_qn("office", "document"))
    doc_el.set(_qn("office", "version"), version)
    doc_el.set(_qn("office", "mimetype"), _MIMETYPE)

    # office:body > office:text
    body_el = ET.SubElement(doc_el, _qn("office", "body"))
    text_el = ET.SubElement(body_el, _qn("office", "text"))

    # Emit in document order if content sequence is present (R55 TC-0060)
    content = document.get("content")
    if content is not None:
        for item in content:
            kind = item.get("kind")
            data = item.get("data", {})
            if kind == "block":
                _write_block(text_el, data)
            elif kind == "list":
                _write_list(text_el, data)
            elif kind == "table":
                _write_table(text_el, data)
    else:
        # Legacy path: blocks → lists → tables (R54 and earlier)
        for block in blocks:
            _write_block(text_el, block)
        for lst in lists:
            _write_list(text_el, lst)
        for table in tables:
            _write_table(text_el, table)

    # Serialize
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    body = ET.tostring(doc_el, encoding="unicode", xml_declaration=False)
    return xml_declaration + body


def write_fodt(document: dict[str, Any], file_path: str | Path) -> None:
    """Write a neutral model document dict to a FODT file.

    Args:
        document: dict following the fodt neutral model schema.
                  Accepts both ``blocks`` (canonical) and ``paragraphs`` (legacy) keys.
        file_path: destination path for the .fodt file.
    """
    xml_content = document_to_xml(document)
    path = Path(file_path)
    path.write_text(xml_content, encoding="utf-8", newline="\n")
