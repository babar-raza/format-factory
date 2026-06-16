"""Tests for odt_has_headings and odt_max_paragraph_length (Sprint 32)."""
import sys
import zipfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.odt import odt_has_headings, odt_max_paragraph_length

_NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
_NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def _make_odt(tmp_path, name, paragraphs=(), headings=()):
    """Create a minimal ODT. paragraphs and headings are sequences of text strings."""
    para_xml = "".join(
        f'<text:p xmlns:text="{_NS_TEXT}">{p}</text:p>' for p in paragraphs
    )
    heading_xml = "".join(
        f'<text:h xmlns:text="{_NS_TEXT}" text:outline-level="1">{h}</text:h>'
        for h in headings
    )
    content_xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{_NS_OFFICE}" xmlns:text="{_NS_TEXT}">'
        f'<office:body><office:text>{heading_xml}{para_xml}</office:text></office:body>'
        f'</office:document-content>'
    )
    path = tmp_path / f"{name}.odt"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        zf.writestr("content.xml", content_xml)
    return path


class TestOdtHasHeadings:
    def test_return_type(self, tmp_path):
        f = _make_odt(tmp_path, "rt", paragraphs=["hello"])
        assert isinstance(odt_has_headings(f), bool)

    def test_true_with_heading(self, tmp_path):
        f = _make_odt(tmp_path, "wh", headings=["Title"])
        assert odt_has_headings(f) is True

    def test_false_no_headings(self, tmp_path):
        f = _make_odt(tmp_path, "nh", paragraphs=["just text"])
        assert odt_has_headings(f) is False

    def test_multiple_headings_true(self, tmp_path):
        f = _make_odt(tmp_path, "mh", headings=["H1", "H2", "H3"])
        assert odt_has_headings(f) is True

    def test_empty_doc_false(self, tmp_path):
        f = _make_odt(tmp_path, "ed")
        assert odt_has_headings(f) is False


class TestOdtMaxParagraphLength:
    def test_return_type(self, tmp_path):
        f = _make_odt(tmp_path, "rt2", paragraphs=["hello"])
        assert isinstance(odt_max_paragraph_length(f), int)

    def test_exact_length(self, tmp_path):
        f = _make_odt(tmp_path, "el", paragraphs=["hello"])
        assert odt_max_paragraph_length(f) == 5

    def test_max_of_two(self, tmp_path):
        # "hi"=2, "hello world"=11 -> max=11
        f = _make_odt(tmp_path, "m2", paragraphs=["hi", "hello world"])
        assert odt_max_paragraph_length(f) == 11

    def test_empty_doc_zero(self, tmp_path):
        f = _make_odt(tmp_path, "zero")
        assert odt_max_paragraph_length(f) == 0

    def test_nonnegative(self, tmp_path):
        f = _make_odt(tmp_path, "nn", paragraphs=["x"])
        assert odt_max_paragraph_length(f) >= 0
