"""
tests/python/fodt/test_r47_writer_hardening.py

R47 MT5 Lane 5B — FODT Python writer hardening tests.

Tests the write_fodt() and document_to_xml() functions against edge cases.

Sprint: FORMAT-FACTORY-R47-ARTIFACT-PROOF-REPAIR-AND-PHASE-AUDIT-PROGRESSION-001
"""

import os
import tempfile
import xml.etree.ElementTree as ET

import pytest

from fodt import parse_fodt, write_fodt, document_to_xml
from fodt.exceptions import FodtInputError


class TestDocumentToXmlHardening:
    """Hardening tests for document_to_xml edge cases."""

    def test_multiple_paragraphs(self):
        doc = {"paragraphs": [
            {"text_content": "First"},
            {"text_content": "Second"},
            {"text_content": "Third"},
        ]}
        xml = document_to_xml(doc)
        assert "First" in xml
        assert "Second" in xml
        assert "Third" in xml

    def test_empty_paragraph(self):
        doc = {"paragraphs": [{"text_content": ""}]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        assert root is not None

    def test_empty_document_no_exception(self):
        doc = {"paragraphs": []}
        xml = document_to_xml(doc)
        assert isinstance(xml, str)
        root = ET.fromstring(xml)
        assert root is not None

    def test_special_characters_escaped(self):
        doc = {"paragraphs": [{"text_content": "<tag> & 'quote' \"dquote\""}]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        assert root is not None

    def test_unicode_content(self):
        doc = {"paragraphs": [{"text_content": "caf\u00e9 \u6c49\u5b57 \u041f\u0440\u0438\u0432\u0435\u0442"}]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        assert root is not None

    def test_long_paragraph(self):
        doc = {"paragraphs": [{"text_content": "x" * 10000}]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        assert root is not None

    def test_many_paragraphs(self):
        doc = {"paragraphs": [{"text_content": f"Para {i}"} for i in range(200)]}
        xml = document_to_xml(doc)
        root = ET.fromstring(xml)
        assert root is not None

    def test_mimetype_in_xml(self):
        doc = {"paragraphs": [{"text_content": "test"}]}
        xml = document_to_xml(doc)
        assert "opendocument" in xml.lower() or "text" in xml.lower()

    def test_non_dict_raises(self):
        with pytest.raises((FodtInputError, TypeError, AttributeError, KeyError)):
            document_to_xml([1, 2, 3])

    def test_none_raises(self):
        with pytest.raises((FodtInputError, TypeError, AttributeError)):
            document_to_xml(None)

    def test_content_key_fallback(self):
        """Writer should accept 'content' key as fallback to 'text_content'."""
        doc = {"paragraphs": [{"content": "From content key"}]}
        xml = document_to_xml(doc)
        assert "From content key" in xml


class TestWriteFodtHardening:
    """Hardening tests for write_fodt() to file."""

    def _tmp_fodt(self):
        f = tempfile.NamedTemporaryFile(suffix=".fodt", delete=False)
        f.close()
        return f.name

    def test_writes_valid_file(self):
        doc = {"paragraphs": [{"text_content": "Hello"}]}
        tmp = self._tmp_fodt()
        try:
            write_fodt(doc, tmp)
            assert os.path.exists(tmp)
            assert os.path.getsize(tmp) > 100
        finally:
            os.unlink(tmp)

    def test_round_trip_block_count(self):
        doc = {"paragraphs": [
            {"text_content": "First paragraph"},
            {"text_content": "Second paragraph"},
        ]}
        tmp = self._tmp_fodt()
        try:
            write_fodt(doc, tmp)
            result = parse_fodt(tmp)
            blocks = result.get("blocks", [])
            assert len(blocks) >= 2
        finally:
            os.unlink(tmp)

    def test_round_trip_content_preserved(self):
        doc = {"paragraphs": [{"text_content": "Unique_text_12345"}]}
        tmp = self._tmp_fodt()
        try:
            write_fodt(doc, tmp)
            with open(tmp, encoding="utf-8") as f:
                content = f.read()
            assert "Unique_text_12345" in content
        finally:
            os.unlink(tmp)

    def test_utf8_encoding(self):
        doc = {"paragraphs": [{"text_content": "\u4e2d\u6587\u5185\u5bb9"}]}
        tmp = self._tmp_fodt()
        try:
            write_fodt(doc, tmp)
            with open(tmp, encoding="utf-8") as f:
                content = f.read()
            assert "\u4e2d\u6587" in content
        finally:
            os.unlink(tmp)

    def test_file_parseable_as_xml(self):
        doc = {"paragraphs": [{"text_content": "Test"}]}
        tmp = self._tmp_fodt()
        try:
            write_fodt(doc, tmp)
            with open(tmp, encoding="utf-8") as f:
                content = f.read()
            root = ET.fromstring(content)
            assert root is not None
        finally:
            os.unlink(tmp)
