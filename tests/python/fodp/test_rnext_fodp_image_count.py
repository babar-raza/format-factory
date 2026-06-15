"""Tests for fodp_image_count — counts draw:image elements in FODP files."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import fodp_image_count  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FODP_HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
    ' xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"'
    ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
    ' xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"'
    ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
    ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    ' office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml">'
    '<office:body><office:presentation>'
)
_FODP_FOOTER = "</office:presentation></office:body></office:document>"


def _make_fodp(slides_xml: str) -> Path:
    """Write a minimal FODP file and return its path."""
    content = _FODP_HEADER + slides_xml + _FODP_FOOTER
    tmp = tempfile.NamedTemporaryFile(suffix=".fodp", delete=False, mode="w", encoding="utf-8")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBasicImageCount:
    """Basic counting of draw:image elements."""

    def test_no_images(self):
        path = _make_fodp('<draw:page draw:name="S1"></draw:page>')
        assert fodp_image_count(path) == 0

    def test_single_image(self):
        xml = (
            '<draw:page draw:name="S1">'
            '<draw:frame><draw:image xlink:href="img1.png"/></draw:frame>'
            '</draw:page>'
        )
        path = _make_fodp(xml)
        assert fodp_image_count(path) == 1

    def test_multiple_images_one_slide(self):
        xml = (
            '<draw:page draw:name="S1">'
            '<draw:frame><draw:image xlink:href="img1.png"/></draw:frame>'
            '<draw:frame><draw:image xlink:href="img2.png"/></draw:frame>'
            '<draw:frame><draw:image xlink:href="img3.png"/></draw:frame>'
            '</draw:page>'
        )
        path = _make_fodp(xml)
        assert fodp_image_count(path) == 3

    def test_images_across_slides(self):
        xml = (
            '<draw:page draw:name="S1">'
            '<draw:frame><draw:image xlink:href="a.png"/></draw:frame>'
            '</draw:page>'
            '<draw:page draw:name="S2">'
            '<draw:frame><draw:image xlink:href="b.png"/></draw:frame>'
            '<draw:frame><draw:image xlink:href="c.png"/></draw:frame>'
            '</draw:page>'
        )
        path = _make_fodp(xml)
        assert fodp_image_count(path) == 3


class TestMixedContent:
    """Images mixed with text shapes."""

    def test_image_and_text_frames(self):
        xml = (
            '<draw:page draw:name="S1">'
            '<draw:frame><draw:image xlink:href="logo.png"/></draw:frame>'
            '<draw:frame><draw:text-box><text:p>Hello</text:p></draw:text-box></draw:frame>'
            '</draw:page>'
        )
        path = _make_fodp(xml)
        assert fodp_image_count(path) == 1

    def test_empty_presentation(self):
        path = _make_fodp("")
        assert fodp_image_count(path) == 0


class TestReturnType:
    """Verify return type is int."""

    def test_returns_int(self):
        path = _make_fodp('<draw:page draw:name="S1"></draw:page>')
        result = fodp_image_count(path)
        assert isinstance(result, int)


class TestFromBytes:
    """Test passing bytes directly."""

    def test_bytes_input(self):
        xml = (
            '<draw:page draw:name="S1">'
            '<draw:frame><draw:image xlink:href="x.png"/></draw:frame>'
            '</draw:page>'
        )
        content = _FODP_HEADER + xml + _FODP_FOOTER
        assert fodp_image_count(content.encode("utf-8")) == 1
