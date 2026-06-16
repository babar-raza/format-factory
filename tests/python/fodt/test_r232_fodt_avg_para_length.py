"""Tests for fodt_average_paragraph_length (Sprint 22)."""
import pytest, tempfile, os
from src.python.fodt import fodt_average_paragraph_length


@pytest.fixture
def fodt_file(tmp_path):
    """Create a minimal FODT file with paragraphs."""
    def _make(paragraphs):
        p = tmp_path / "test.fodt"
        paras = "".join(f'<text:p text:style-name="Standard">{t}</text:p>' for t in paragraphs)
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.text">
<office:body><office:text>{paras}</office:text></office:body>
</office:document>"""
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _make


class TestFodtAverageParagraphLength:
    def test_single_paragraph(self, fodt_file):
        path = fodt_file(["Hello world"])
        avg = fodt_average_paragraph_length(path)
        assert isinstance(avg, float)

    def test_multiple_paragraphs(self, fodt_file):
        path = fodt_file(["ab", "abcd"])
        avg = fodt_average_paragraph_length(path)
        assert avg > 0.0

    def test_empty_file(self, fodt_file):
        path = fodt_file([])
        avg = fodt_average_paragraph_length(path)
        assert avg == 0.0

    def test_return_type(self, fodt_file):
        path = fodt_file(["test"])
        assert isinstance(fodt_average_paragraph_length(path), float)

    def test_non_negative(self, fodt_file):
        path = fodt_file(["x"])
        assert fodt_average_paragraph_length(path) >= 0.0
