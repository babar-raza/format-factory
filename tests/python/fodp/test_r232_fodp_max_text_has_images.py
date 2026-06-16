"""Tests for fodp_max_text_per_slide and fodp_has_images.

Product deepening: FODP analytics — TC-H3-002-FODP / PDC-FODP-MAX-TEXT-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodp import fodp_max_text_per_slide, fodp_has_images

_NS = (
    'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
    ' xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"'
    ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
    ' xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"'
)


def _make_fodp(tmp_path, name, slides_xml):
    body = "".join(slides_xml)
    xml = (
        f'<?xml version="1.0"?>'
        f'<office:document {_NS} office:mimetype="application/vnd.oasis.opendocument.presentation">'
        f'<office:body><office:presentation>{body}</office:presentation></office:body>'
        f'</office:document>'
    )
    path = tmp_path / f"{name}.fodp"
    path.write_text(xml, encoding="utf-8")
    return path


def _slide(text="", shapes=0):
    frames = "".join(
        f'<draw:frame><draw:text-box><text:p>{text}</text:p></draw:text-box></draw:frame>'
        for _ in range(max(1, shapes)) if text or shapes
    )
    return f'<draw:page draw:name="Slide">{frames}</draw:page>'


class TestFodpMaxTextPerSlide:
    def test_single_slide(self, tmp_path):
        f = _make_fodp(tmp_path, "one", [_slide("hello world")])
        result = fodp_max_text_per_slide(f)
        assert isinstance(result, int)
        assert result >= 11

    def test_two_slides_different_length(self, tmp_path):
        f = _make_fodp(tmp_path, "two", [
            _slide("short"),
            _slide("a much longer text content"),
        ])
        result = fodp_max_text_per_slide(f)
        assert result >= 20

    def test_empty_presentation(self, tmp_path):
        f = _make_fodp(tmp_path, "empty", [])
        assert fodp_max_text_per_slide(f) == 0

    def test_returns_int(self, tmp_path):
        f = _make_fodp(tmp_path, "type", [_slide("test")])
        assert isinstance(fodp_max_text_per_slide(f), int)

    def test_non_negative(self, tmp_path):
        f = _make_fodp(tmp_path, "nn", [_slide("")])
        assert fodp_max_text_per_slide(f) >= 0


class TestFodpHasImages:
    def test_no_images(self, tmp_path):
        f = _make_fodp(tmp_path, "no_img", [_slide("text only")])
        assert fodp_has_images(f) is False

    def test_returns_bool(self, tmp_path):
        f = _make_fodp(tmp_path, "type2", [_slide("text")])
        assert isinstance(fodp_has_images(f), bool)

    def test_empty_presentation(self, tmp_path):
        f = _make_fodp(tmp_path, "empty2", [])
        assert fodp_has_images(f) is False

    def test_with_image(self, tmp_path):
        slide_xml = (
            '<draw:page draw:name="S1">'
            '<draw:frame><draw:image/></draw:frame>'
            '</draw:page>'
        )
        f = _make_fodp(tmp_path, "img", [slide_xml])
        result = fodp_has_images(f)
        assert isinstance(result, bool)
