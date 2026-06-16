"""Tests for fodp_slide_text_density (Sprint 22)."""
import pytest
from src.python.fodp import fodp_slide_text_density


@pytest.fixture
def fodp_file(tmp_path):
    def _make(slides_text):
        p = tmp_path / "test.fodp"
        slides = ""
        for text in slides_text:
            slides += f"""<draw:page draw:name="S" draw:style-name="dp1"
              draw:master-page-name="Default"
              xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
              xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0">
              <draw:frame><draw:text-box>
              <text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">{text}</text:p>
              </draw:text-box></draw:frame></draw:page>"""
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  office:mimetype="application/vnd.oasis.opendocument.presentation">
<office:body><office:presentation>{slides}</office:presentation></office:body>
</office:document>"""
        p.write_text(content, encoding="utf-8")
        return str(p)
    return _make


class TestFodpSlideTextDensity:
    def test_single_slide(self, fodp_file):
        path = fodp_file(["Hello world"])
        d = fodp_slide_text_density(path)
        assert isinstance(d, float)
        assert d > 0.0

    def test_multiple_slides(self, fodp_file):
        path = fodp_file(["ab", "abcdef"])
        d = fodp_slide_text_density(path)
        assert d > 0.0

    def test_return_type(self, fodp_file):
        path = fodp_file(["test"])
        assert isinstance(fodp_slide_text_density(path), float)

    def test_non_negative(self, fodp_file):
        path = fodp_file(["x"])
        assert fodp_slide_text_density(path) >= 0.0

    def test_empty_slides(self, fodp_file):
        path = fodp_file(["", ""])
        d = fodp_slide_text_density(path)
        assert d == 0.0
