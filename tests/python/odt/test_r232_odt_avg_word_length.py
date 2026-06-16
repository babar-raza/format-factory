"""Tests for odt_average_word_length and odt_unique_word_count.

Product deepening: ODT analytics — TC-H3-002-ODT / PDC-ODT-AVG-WORD-001.
"""
import sys
import zipfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.odt import (
    odt_average_word_length,
    odt_unique_word_count,
)


def _make_odt(tmp_path, name, paragraphs):
    """Create a minimal ODT file with given paragraph texts."""
    ns_office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    ns_text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    paras = "".join(
        f'<text:p xmlns:text="{ns_text}">{p}</text:p>' for p in paragraphs
    )
    content_xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{ns_office}" xmlns:text="{ns_text}">'
        f'<office:body><office:text>{paras}</office:text></office:body>'
        f'</office:document-content>'
    )
    path = tmp_path / f"{name}.odt"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        zf.writestr("content.xml", content_xml)
    return path


class TestOdtAverageWordLength:
    def test_single_word(self, tmp_path):
        f = _make_odt(tmp_path, "one", ["hello"])
        assert odt_average_word_length(f) == 5.0

    def test_two_words(self, tmp_path):
        f = _make_odt(tmp_path, "two", ["hi there"])
        # "hi"=2, "there"=5 → avg=3.5
        assert odt_average_word_length(f) == 3.5

    def test_multiple_paragraphs(self, tmp_path):
        f = _make_odt(tmp_path, "multi", ["abc def", "ghij"])
        # "abc"=3, "def"=3, "ghij"=4 → avg=10/3≈3.333
        result = odt_average_word_length(f)
        assert abs(result - 10 / 3) < 0.01

    def test_empty_document(self, tmp_path):
        f = _make_odt(tmp_path, "empty", [])
        assert odt_average_word_length(f) == 0.0

    def test_empty_paragraph(self, tmp_path):
        f = _make_odt(tmp_path, "blank", [""])
        assert odt_average_word_length(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _make_odt(tmp_path, "type", ["word"])
        assert isinstance(odt_average_word_length(f), float)


class TestOdtUniqueWordCount:
    def test_single_word(self, tmp_path):
        f = _make_odt(tmp_path, "u1", ["hello"])
        assert odt_unique_word_count(f) == 1

    def test_duplicate_words(self, tmp_path):
        f = _make_odt(tmp_path, "u2", ["hello hello world"])
        assert odt_unique_word_count(f) == 2

    def test_case_insensitive(self, tmp_path):
        f = _make_odt(tmp_path, "u3", ["Hello HELLO hello"])
        assert odt_unique_word_count(f) == 1

    def test_across_paragraphs(self, tmp_path):
        f = _make_odt(tmp_path, "u4", ["foo bar", "bar baz"])
        assert odt_unique_word_count(f) == 3

    def test_empty_document(self, tmp_path):
        f = _make_odt(tmp_path, "u5", [])
        assert odt_unique_word_count(f) == 0

    def test_returns_int(self, tmp_path):
        f = _make_odt(tmp_path, "u6", ["test"])
        assert isinstance(odt_unique_word_count(f), int)
