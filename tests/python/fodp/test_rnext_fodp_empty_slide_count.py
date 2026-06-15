"""Tests for fodp_empty_slide_count — counts slides with no shapes or text."""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import fodp_empty_slide_count, fodp_slide_count

# Minimal FODP XML templates
_HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
    ' xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"'
    ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
    ' xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"'
    ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
    ' office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">'
    '<office:body><office:presentation>'
)

_FOOTER = '</office:presentation></office:body></office:document>'


def _empty_slide(name="Slide1"):
    return f'<draw:page draw:name="{name}"></draw:page>'


def _slide_with_shape(name="Slide1", text="Hello"):
    return (
        f'<draw:page draw:name="{name}">'
        f'<draw:frame><text:p>{text}</text:p></draw:frame>'
        f'</draw:page>'
    )


def _fodp(*slides) -> str:
    return _HEADER + "".join(slides) + _FOOTER


class TestEmptyPresentation:
    def test_no_slides(self):
        xml = _fodp()
        assert fodp_empty_slide_count(xml.encode()) == 0

    def test_single_empty_slide(self):
        xml = _fodp(_empty_slide())
        assert fodp_empty_slide_count(xml.encode()) == 1

    def test_multiple_empty_slides(self):
        xml = _fodp(_empty_slide("S1"), _empty_slide("S2"), _empty_slide("S3"))
        assert fodp_empty_slide_count(xml.encode()) == 3


class TestNonEmptySlides:
    def test_single_slide_with_shape(self):
        xml = _fodp(_slide_with_shape())
        assert fodp_empty_slide_count(xml.encode()) == 0

    def test_all_slides_with_shapes(self):
        xml = _fodp(_slide_with_shape("S1"), _slide_with_shape("S2"))
        assert fodp_empty_slide_count(xml.encode()) == 0


class TestMixedContent:
    def test_mixed_empty_and_nonempty(self):
        xml = _fodp(
            _slide_with_shape("S1"),
            _empty_slide("S2"),
            _slide_with_shape("S3"),
            _empty_slide("S4"),
        )
        assert fodp_empty_slide_count(xml.encode()) == 2

    def test_consistency_with_slide_count(self):
        xml = _fodp(
            _slide_with_shape("S1"),
            _empty_slide("S2"),
            _empty_slide("S3"),
        )
        data = xml.encode()
        total = fodp_slide_count(data)
        empty = fodp_empty_slide_count(data)
        assert total == 3
        assert empty == 2
        assert empty <= total


class TestEdgeCases:
    def test_return_type(self):
        xml = _fodp(_empty_slide())
        assert isinstance(fodp_empty_slide_count(xml.encode()), int)
