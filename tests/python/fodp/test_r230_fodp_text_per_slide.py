"""Tests for fodp_text_per_slide and fodp_average_shapes_per_slide.

Product deepening: FODP analytics — TC-H3-001 / PDC-FODP-TEXT-PER-SLIDE-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodp import (
    fodp_text_per_slide,
    fodp_average_shapes_per_slide,
    fodp_slide_count,
    load,
)

SAMPLES = _REPO / "samples" / "by-format" / "fodp"

# Inline minimal XML for synthetic tests
EMPTY_PRES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0">
  <office:body><office:presentation/></office:body>
</office:document>"""

ONE_SLIDE_WITH_TEXT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0">
  <office:body><office:presentation>
    <draw:page draw:name="Slide1">
      <draw:frame><draw:text-box>
        <text:p>Hello World</text:p>
        <text:p>Second line</text:p>
      </draw:text-box></draw:frame>
    </draw:page>
  </office:presentation></office:body>
</office:document>"""

TWO_SLIDES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0">
  <office:body><office:presentation>
    <draw:page draw:name="Slide1">
      <draw:frame><draw:text-box><text:p>First</text:p></draw:text-box></draw:frame>
      <draw:frame><draw:text-box><text:p>Also first</text:p></draw:text-box></draw:frame>
    </draw:page>
    <draw:page draw:name="Slide2">
      <draw:frame><draw:text-box><text:p>Second</text:p></draw:text-box></draw:frame>
    </draw:page>
  </office:presentation></office:body>
</office:document>"""


class TestFodpTextPerSlide:
    def test_empty_presentation(self):
        result = fodp_text_per_slide(EMPTY_PRES_XML)
        assert result == []

    def test_single_slide_with_text(self):
        result = fodp_text_per_slide(ONE_SLIDE_WITH_TEXT_XML)
        assert len(result) == 1
        assert "Hello World" in result[0]
        assert "Second line" in result[0]

    def test_two_slides(self):
        result = fodp_text_per_slide(TWO_SLIDES_XML)
        assert len(result) == 2
        assert "First" in result[0]
        assert "Second" in result[1]

    def test_returns_list_of_strings(self):
        result = fodp_text_per_slide(ONE_SLIDE_WITH_TEXT_XML)
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_from_file_two_slides_basic(self):
        path = SAMPLES / "two-slides-basic.fodp"
        if path.exists():
            result = fodp_text_per_slide(path)
            assert isinstance(result, list)
            assert len(result) == fodp_slide_count(path)

    def test_from_file_minimal_presentation(self):
        path = SAMPLES / "minimal-presentation.fodp"
        if path.exists():
            result = fodp_text_per_slide(path)
            assert isinstance(result, list)


class TestFodpAverageShapesPerSlide:
    def test_empty_presentation(self):
        result = fodp_average_shapes_per_slide(EMPTY_PRES_XML)
        assert result == 0.0

    def test_single_slide_returns_float(self):
        result = fodp_average_shapes_per_slide(ONE_SLIDE_WITH_TEXT_XML)
        assert isinstance(result, float)

    def test_two_slides_average(self):
        result = fodp_average_shapes_per_slide(TWO_SLIDES_XML)
        assert isinstance(result, float)
        assert result >= 0.0

    def test_from_file_two_slides_basic(self):
        path = SAMPLES / "two-slides-basic.fodp"
        if path.exists():
            result = fodp_average_shapes_per_slide(path)
            assert isinstance(result, float)
            assert result >= 0.0

    def test_matches_manual_calculation(self):
        model = load(TWO_SLIDES_XML)
        pages = model.get("pages", [])
        if pages:
            expected = sum(p.get("shape_count", 0) for p in pages) / len(pages)
            actual = fodp_average_shapes_per_slide(TWO_SLIDES_XML)
            assert abs(actual - expected) < 0.001
