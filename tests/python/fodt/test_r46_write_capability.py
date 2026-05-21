"""
R46 MT6: FODT Python write/export capability tests.

Tests that write_fodt() and document_to_xml() correctly serialize
neutral model document dicts to valid FODT XML.
"""

import tempfile
from pathlib import Path

import pytest

from fodt import write_fodt, document_to_xml, parse_fodt
from fodt.exceptions import FodtInputError


def _minimal_document():
    return {
        "paragraphs": [
            {"text_content": "Hello World"},
            {"text_content": "Second paragraph"},
        ]
    }


class TestDocumentToXml:
    def test_returns_string(self):
        xml = document_to_xml(_minimal_document())
        assert isinstance(xml, str)

    def test_has_xml_declaration(self):
        xml = document_to_xml(_minimal_document())
        assert xml.startswith("<?xml")

    def test_has_office_document_root(self):
        xml = document_to_xml(_minimal_document())
        assert "office:document" in xml

    def test_has_office_text(self):
        xml = document_to_xml(_minimal_document())
        assert "office:text" in xml

    def test_has_text_p_elements(self):
        xml = document_to_xml(_minimal_document())
        assert "text:p" in xml

    def test_paragraph_content_in_output(self):
        xml = document_to_xml(_minimal_document())
        assert "Hello World" in xml

    def test_second_paragraph_in_output(self):
        xml = document_to_xml(_minimal_document())
        assert "Second paragraph" in xml

    def test_raises_on_non_dict(self):
        with pytest.raises(FodtInputError):
            document_to_xml("not a dict")

    def test_empty_document_valid_xml(self):
        xml = document_to_xml({"paragraphs": []})
        assert "office:document" in xml

    def test_mimetype_in_output(self):
        xml = document_to_xml(_minimal_document())
        assert "vnd.oasis.opendocument.text" in xml


class TestWriteFodt:
    def test_writes_file(self, tmp_path):
        out = tmp_path / "test.fodt"
        write_fodt(_minimal_document(), out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_written_file_is_utf8(self, tmp_path):
        out = tmp_path / "test.fodt"
        write_fodt(_minimal_document(), out)
        content = out.read_text(encoding="utf-8")
        assert "Hello World" in content

    def test_round_trip_parse_written_file(self, tmp_path):
        """Write a document, then parse it back — must not error."""
        out = tmp_path / "round-trip.fodt"
        write_fodt(_minimal_document(), out)
        result = parse_fodt(str(out))
        assert result.get("error") is None, f"Parse error: {result.get('error')}"
        assert len(result.get("blocks", [])) >= 1

    def test_round_trip_content_preserved(self, tmp_path):
        """Paragraph text must be preserved through write-parse round-trip."""
        doc = {"paragraphs": [{"text_content": "UniqueContent12345"}]}
        out = tmp_path / "rt.fodt"
        write_fodt(doc, out)
        content = out.read_text(encoding="utf-8")
        assert "UniqueContent12345" in content

    def test_multiple_paragraphs(self, tmp_path):
        """Multiple paragraphs are written correctly."""
        doc = {
            "paragraphs": [
                {"text_content": "Para1"},
                {"text_content": "Para2"},
                {"text_content": "Para3"},
            ]
        }
        out = tmp_path / "multi.fodt"
        write_fodt(doc, out)
        result = parse_fodt(str(out))
        assert len(result.get("blocks", [])) >= 3
