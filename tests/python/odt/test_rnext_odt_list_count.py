"""Tests for odt_list_count — counts top-level text:list elements in ODT files."""

from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import odt_list_count  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NS_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
_NS_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"

_CONTENT_HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    f'<office:document-content xmlns:office="{_NS_OFFICE}" xmlns:text="{_NS_TEXT}">'
    "<office:body><office:text>"
)
_CONTENT_FOOTER = "</office:text></office:body></office:document-content>"

_MIMETYPE = "application/vnd.oasis.opendocument.text"


def _make_odt(body_xml: str) -> Path:
    """Create a minimal .odt ZIP with the given body XML inside content.xml."""
    content = _CONTENT_HEADER + body_xml + _CONTENT_FOOTER
    tmp = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
    tmp.close()
    with zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr("mimetype", _MIMETYPE)
        zf.writestr("content.xml", content)
    return Path(tmp.name)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBasicListCount:
    """Basic counting of top-level text:list elements."""

    def test_no_lists(self):
        path = _make_odt("<text:p>Hello world</text:p>")
        assert odt_list_count(path) == 0

    def test_single_list(self):
        xml = (
            "<text:list>"
            "<text:list-item><text:p>Item 1</text:p></text:list-item>"
            "<text:list-item><text:p>Item 2</text:p></text:list-item>"
            "</text:list>"
        )
        path = _make_odt(xml)
        assert odt_list_count(path) == 1

    def test_multiple_lists(self):
        xml = (
            "<text:list>"
            "<text:list-item><text:p>A</text:p></text:list-item>"
            "</text:list>"
            "<text:p>Separator paragraph</text:p>"
            "<text:list>"
            "<text:list-item><text:p>B</text:p></text:list-item>"
            "</text:list>"
            "<text:list>"
            "<text:list-item><text:p>C</text:p></text:list-item>"
            "</text:list>"
        )
        path = _make_odt(xml)
        assert odt_list_count(path) == 3


class TestMixedContent:
    """Lists mixed with paragraphs and headings."""

    def test_list_with_paragraphs(self):
        xml = (
            "<text:p>Intro</text:p>"
            "<text:list>"
            "<text:list-item><text:p>First</text:p></text:list-item>"
            "</text:list>"
            "<text:p>Middle</text:p>"
            "<text:list>"
            "<text:list-item><text:p>Second</text:p></text:list-item>"
            "</text:list>"
            "<text:p>End</text:p>"
        )
        path = _make_odt(xml)
        assert odt_list_count(path) == 2


class TestEdgeCases:
    """Edge cases."""

    def test_empty_document(self):
        path = _make_odt("")
        assert odt_list_count(path) == 0

    def test_empty_list(self):
        path = _make_odt("<text:list></text:list>")
        assert odt_list_count(path) == 1

    def test_nested_lists_count_only_top_level(self):
        xml = (
            "<text:list>"
            "<text:list-item>"
            "<text:p>Outer</text:p>"
            "<text:list>"
            "<text:list-item><text:p>Inner</text:p></text:list-item>"
            "</text:list>"
            "</text:list-item>"
            "</text:list>"
        )
        path = _make_odt(xml)
        assert odt_list_count(path) == 1


class TestReturnType:
    """Verify return type."""

    def test_returns_int(self):
        path = _make_odt("")
        result = odt_list_count(path)
        assert isinstance(result, int)
