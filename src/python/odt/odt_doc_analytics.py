"""
ODT document analytics — file-path based analytics derived from parse_odt output.

Provides analytics computed from the document model produced by odt_parser.
No spec_qname claim — analytics modules do not represent ODT element types.
"""
from __future__ import annotations

from pathlib import Path

from .odt_parser import parse_odt

spec_qname = "office:document-content"
spec_fact_ref = "FACT-ODT-001"


def odt_paragraph_count(source: "str | bytes | Path") -> int:
    """Return count of text paragraphs in the ODT document.

    Spec: ODF 1.3 text:p element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return doc.get("paragraph_count", 0)


def odt_heading_count(source: "str | bytes | Path") -> int:
    """Return count of heading elements in the ODT document.

    Spec: ODF 1.3 text:h element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return doc.get("heading_count", 0)


def odt_element_count(source: "str | bytes | Path") -> int:
    """Return total element count (paragraphs + headings) in the ODT document.

    Spec: ODF 1.3 text:p and text:h elements (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return doc.get("element_count", 0)


def odt_is_ok(source: "str | bytes | Path") -> bool:
    """Return True if parse_odt succeeded without errors.

    Spec: ODF 1.3 office:document-content (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return bool(doc.get("ok", False))


def odt_first_paragraph_text(source: "str | bytes | Path") -> str:
    """Return text of the first paragraph. Empty string if no paragraphs.

    Spec: ODF 1.3 text:p element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    paragraphs = doc.get("paragraphs", [])
    if not paragraphs:
        return ""
    return paragraphs[0].get("text", "")


def odt_total_text_length(source: "str | bytes | Path") -> int:
    """Return total character count across all paragraph texts.

    Spec: ODF 1.3 text:p element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return sum(len(p.get("text", "")) for p in doc.get("paragraphs", []))
