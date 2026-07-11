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


def odt_has_paragraphs(source: "str | bytes | Path") -> bool:
    """Return True if the ODT document contains at least one paragraph.

    Spec: ODF 1.3 text:p element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return doc.get("paragraph_count", 0) > 0


def odt_has_headings(source: "str | bytes | Path") -> bool:
    """Return True if the ODT document contains at least one heading.

    Spec: ODF 1.3 text:h element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return doc.get("heading_count", 0) > 0


def odt_avg_paragraph_length(source: "str | bytes | Path") -> float:
    """Return average character length of all paragraphs. 0.0 if no paragraphs.

    Spec: ODF 1.3 text:p element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    paras = doc.get("paragraphs", [])
    if not paras:
        return 0.0
    return sum(len(p.get("text", "")) for p in paras) / len(paras)


def odt_max_paragraph_length(source: "str | bytes | Path") -> int:
    """Return maximum character length among all paragraphs. 0 if no paragraphs.

    Spec: ODF 1.3 text:p element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    paras = doc.get("paragraphs", [])
    if not paras:
        return 0
    return max(len(p.get("text", "")) for p in paras)


def odt_paragraph_texts(source: "str | bytes | Path") -> list:
    """Return list of all paragraph text strings in document order.

    Spec: ODF 1.3 text:p element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return [p.get("text", "") for p in doc.get("paragraphs", [])]


def odt_is_single_paragraph(source: "str | bytes | Path") -> bool:
    """Return True if the document contains exactly one paragraph.

    Spec: ODF 1.3 text:p element (FACT-ODT-001)
    """
    doc = parse_odt(source)
    return doc.get("paragraph_count", 0) == 1
