"""Tests for fodt_paragraph_count and fodt_word_count.

Product deepening: FODT analytics — TC-H3-002-FODT / PDC-FODT-PARA-COUNT-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_paragraph_count, fodt_word_count

_NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
_NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def _make_fodt(tmp_path, name, paragraphs):
    """Create a FODT file by writing raw XML."""
    paras = "".join(
        f'<text:p xmlns:text="{_NS_TEXT}">{p}</text:p>' for p in paragraphs
    )
    xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document xmlns:office="{_NS_OFFICE}" xmlns:text="{_NS_TEXT}"'
        f' office:version="1.3"'
        f' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
        f'<office:body><office:text>{paras}</office:text></office:body>'
        f'</office:document>'
    )
    path = tmp_path / f"{name}.fodt"
    path.write_text(xml, encoding="utf-8")
    return path


class TestFodtParagraphCount:
    def test_single_paragraph(self, tmp_path):
        f = _make_fodt(tmp_path, "one", ["hello world"])
        assert fodt_paragraph_count(f) == 1

    def test_three_paragraphs(self, tmp_path):
        f = _make_fodt(tmp_path, "three", ["a", "b", "c"])
        assert fodt_paragraph_count(f) == 3

    def test_empty_document(self, tmp_path):
        f = _make_fodt(tmp_path, "empty", [])
        assert fodt_paragraph_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _make_fodt(tmp_path, "type", ["test"])
        assert isinstance(fodt_paragraph_count(f), int)

    def test_empty_paragraphs(self, tmp_path):
        f = _make_fodt(tmp_path, "blanks", ["", "", ""])
        assert fodt_paragraph_count(f) == 3


class TestFodtWordCount:
    def test_two_words(self, tmp_path):
        f = _make_fodt(tmp_path, "two", ["hello world"])
        assert fodt_word_count(f) == 2

    def test_multiple_paragraphs(self, tmp_path):
        f = _make_fodt(tmp_path, "multi", ["one two", "three four five"])
        assert fodt_word_count(f) == 5

    def test_empty_document(self, tmp_path):
        f = _make_fodt(tmp_path, "empty2", [])
        assert fodt_word_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _make_fodt(tmp_path, "type2", ["word"])
        assert isinstance(fodt_word_count(f), int)

    def test_single_word(self, tmp_path):
        f = _make_fodt(tmp_path, "single", ["hello"])
        assert fodt_word_count(f) == 1
