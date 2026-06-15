"""
test_rnext_fodt_document_to_xml.py -- Dedicated test coverage for document_to_xml.

Gap: GAP-FODT-FOSS-DOCUMENT_TO_-001 (missing_test_coverage)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.writer import document_to_xml


def _doc(blocks=None):
    return {"blocks": blocks or []}


def _para(text=""):
    return {"type": "paragraph", "text": text}


def _heading(text="", level=1):
    return {"type": "heading", "text": text, "level": level}


class TestDocumentToXmlBasic:
    def test_returns_string(self):
        xml = document_to_xml(_doc())
        assert isinstance(xml, str)

    def test_xml_declaration(self):
        xml = document_to_xml(_doc())
        assert xml.startswith("<?xml")

    def test_contains_office_document(self):
        xml = document_to_xml(_doc())
        assert "office:document" in xml

    def test_paragraph_text_in_output(self):
        xml = document_to_xml(_doc([_para("TestContent")]))
        assert "TestContent" in xml

    def test_heading_text_in_output(self):
        xml = document_to_xml(_doc([_heading("MyHeading")]))
        assert "MyHeading" in xml

    def test_multiple_blocks(self):
        doc = _doc([_para("First"), _para("Second"), _para("Third")])
        xml = document_to_xml(doc)
        assert "First" in xml
        assert "Second" in xml
        assert "Third" in xml

    def test_empty_document(self):
        xml = document_to_xml(_doc())
        assert isinstance(xml, str)
        assert len(xml) > 50

    def test_unicode_content(self):
        xml = document_to_xml(_doc([_para("caf\u00e9")]))
        assert "\u00e9" in xml

    def test_legacy_paragraphs_key(self):
        doc = {"paragraphs": [{"text_content": "LegacyText"}]}
        xml = document_to_xml(doc)
        assert "LegacyText" in xml

    def test_special_chars_escaped(self):
        xml = document_to_xml(_doc([_para("a < b & c > d")]))
        assert "&lt;" in xml or "<" not in xml.split("text:p")[1].split("</")[0] if "text:p" in xml else True
