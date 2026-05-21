"""
writer.py -- FODT serializer for format-factory-fodt.

Writes a neutral model document dict to a FODT (Flat OpenDocument Text) XML file.

Public API:
  write_fodt(document, file_path)  -- serialize document to FODT file
  document_to_xml(document)        -- serialize document to XML string

R46 MT6: Two-product capability deepening. Adds write/export path to FOSS package.

Capability level: alpha-foss-preview (write subset — paragraphs with plain text
content only; headings, lists, tables, and styles are not generated).

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


def _write_paragraph(parent: ET.Element, para: dict[str, Any]) -> None:
    """Append a text:p element for the given neutral model paragraph."""
    para_el = ET.SubElement(parent, _qn("text", "p"))
    content = para.get("text_content", para.get("content", ""))
    para_el.text = str(content) if content is not None else ""


def document_to_xml(document: dict[str, Any]) -> str:
    """Serialize a neutral model document dict to a FODT XML string.

    Args:
        document: dict following the fodt neutral model schema.
                  Required keys: paragraphs (list of paragraph dicts).
                  Optional keys: odf_version_attr.

    Returns:
        UTF-8 XML string (str) representing a valid FODT document.
    """
    if not isinstance(document, dict):
        raise FodtInputError("document must be a dict")

    paragraphs = document.get("paragraphs", [])
    if not isinstance(paragraphs, list):
        raise FodtInputError("document['paragraphs'] must be a list")

    version = document.get("odf_version_attr", "1.3")

    # Build root element
    doc_el = ET.Element(_qn("office", "document"))
    doc_el.set(_qn("office", "version"), version)
    doc_el.set(_qn("office", "mimetype"), _MIMETYPE)

    # office:body > office:text
    body_el = ET.SubElement(doc_el, _qn("office", "body"))
    text_el = ET.SubElement(body_el, _qn("office", "text"))

    for para in paragraphs:
        _write_paragraph(text_el, para)

    # Serialize
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    body = ET.tostring(doc_el, encoding="unicode", xml_declaration=False)
    return xml_declaration + body


def write_fodt(document: dict[str, Any], file_path: str | Path) -> None:
    """Write a neutral model document dict to a FODT file.

    Args:
        document: dict following the fodt neutral model schema.
        file_path: destination path for the .fodt file.
    """
    xml_content = document_to_xml(document)
    path = Path(file_path)
    path.write_text(xml_content, encoding="utf-8", newline="\n")
