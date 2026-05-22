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

Capability level: alpha-foss-preview (write subset — paragraphs and headings with plain
text content only; lists, tables, and styles are not generated).

License: Apache-2.0
Package: format-factory-fodt v0.1.0
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .constants import FORMAT_ID, SPEC_VERSION, PACKAGE_VERSION
from .exceptions import FodtInputError

# ODF 1.3 namespace URIs
_NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
}

_MIMETYPE = "application/vnd.oasis.opendocument.text-flat-xml"

# Register namespaces so ET uses the short prefixes
for _prefix, _uri in _NS.items():
    ET.register_namespace(_prefix, _uri)


def _qn(ns_prefix: str, local: str) -> str:
    return f"{{{_NS[ns_prefix]}}}{local}"


def _write_block(parent: ET.Element, block: dict[str, Any]) -> None:
    """Append a text:p or text:h element for the given neutral model block.

    Handles canonical ``blocks`` items (from parser output):
      - type='paragraph' → text:p
      - type='heading'   → text:h with text:outline-level attribute

    Also handles legacy ``paragraphs`` list items (text_content/content keys).

    R49: replaces _write_paragraph to support heading blocks from parser output.
    """
    block_type = block.get("type", "paragraph")
    text = block.get("text", block.get("text_content", block.get("content", "")))
    text = str(text) if text is not None else ""

    if block_type == "heading":
        el = ET.SubElement(parent, _qn("text", "h"))
        level = block.get("heading_level") or 1
        el.set(_qn("text", "outline-level"), str(level))
        el.text = text
    else:
        # paragraph (default)
        el = ET.SubElement(parent, _qn("text", "p"))
        el.text = text


def document_to_xml(document: dict[str, Any]) -> str:
    """Serialize a neutral model document dict to a FODT XML string.

    Accepts both canonical ``blocks`` key (parser output) and legacy
    ``paragraphs`` key. If ``blocks`` is present it takes precedence.

    Args:
        document: dict following the fodt neutral model schema.
                  Canonical key: ``blocks`` (list of block dicts with ``type``/``text``).
                  Legacy key: ``paragraphs`` (list of paragraph dicts with ``text_content``).
                  Optional keys: odf_version_attr.

    Returns:
        UTF-8 XML string (str) representing a valid FODT document.
    """
    if not isinstance(document, dict):
        raise FodtInputError("document must be a dict")

    # Accept blocks (canonical — matches parser output) or paragraphs (legacy alias)
    blocks = document.get("blocks")
    if blocks is None:
        blocks = document.get("paragraphs", [])
    if not isinstance(blocks, list):
        raise FodtInputError("document['blocks'] (or 'paragraphs') must be a list")

    version = document.get("odf_version_attr", "1.3")

    # Build root element
    doc_el = ET.Element(_qn("office", "document"))
    doc_el.set(_qn("office", "version"), version)
    doc_el.set(_qn("office", "mimetype"), _MIMETYPE)

    # office:body > office:text
    body_el = ET.SubElement(doc_el, _qn("office", "body"))
    text_el = ET.SubElement(body_el, _qn("office", "text"))

    for block in blocks:
        _write_block(text_el, block)

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
