"""
tests/python/fodp/test_r220_fodp_slide_titles.py

Sprint: PRODUCT-DEEPENING-CONTINUATION-20260613
Tests for fodp_slide_titles() — return per-slide title list.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import (
    fodp_slide_titles,
    load,
    FodpParseError,
)

SAMPLES = _REPO / "samples" / "by-format" / "fodp"


class TestFodpSlideTitlesFromFile:
    """Test fodp_slide_titles with on-disk .fodp samples."""

    def test_two_slides_returns_two_titles(self):
        result = fodp_slide_titles(SAMPLES / "two-slides-basic.fodp")
        assert len(result) == 2

    def test_two_slides_first_title_is_introduction(self):
        result = fodp_slide_titles(SAMPLES / "two-slides-basic.fodp")
        assert result[0] == "Introduction"

    def test_two_slides_second_title_is_conclusion(self):
        result = fodp_slide_titles(SAMPLES / "two-slides-basic.fodp")
        assert result[1] == "Conclusion"

    def test_title_only_is_empty_presentation(self):
        # title-only.fodp has no draw:page elements (empty presentation)
        result = fodp_slide_titles(SAMPLES / "title-only.fodp")
        assert result == []

    def test_minimal_returns_list(self):
        result = fodp_slide_titles(SAMPLES / "minimal-presentation.fodp")
        assert isinstance(result, list)


class TestFodpSlideTitlesFromXmlString:
    """Test fodp_slide_titles with inline XML strings."""

    TITLED_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml"
    office:version="1.3">
  <office:body>
    <office:presentation>
      <draw:page draw:name="S1">
        <draw:frame presentation:class="title">
          <draw:text-box><text:p>Alpha</text:p></draw:text-box>
        </draw:frame>
      </draw:page>
      <draw:page draw:name="S2">
        <draw:frame presentation:class="body">
          <draw:text-box><text:p>No title here</text:p></draw:text-box>
        </draw:frame>
      </draw:page>
      <draw:page draw:name="S3">
        <draw:frame presentation:class="title">
          <draw:text-box><text:p>Gamma</text:p></draw:text-box>
        </draw:frame>
      </draw:page>
    </office:presentation>
  </office:body>
</office:document>"""

    EMPTY_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
    office:mimetype="application/vnd.oasis.opendocument.presentation-flat-xml"
    office:version="1.3">
  <office:body>
    <office:presentation/>
  </office:body>
</office:document>"""

    def test_three_slides_returns_three_entries(self):
        result = fodp_slide_titles(self.TITLED_XML)
        assert len(result) == 3

    def test_titled_slide_has_string_title(self):
        result = fodp_slide_titles(self.TITLED_XML)
        assert result[0] == "Alpha"

    def test_untitled_slide_has_none(self):
        result = fodp_slide_titles(self.TITLED_XML)
        assert result[1] is None

    def test_third_slide_title(self):
        result = fodp_slide_titles(self.TITLED_XML)
        assert result[2] == "Gamma"

    def test_empty_presentation_returns_empty_list(self):
        result = fodp_slide_titles(self.EMPTY_XML)
        assert result == []

    def test_return_type_is_list(self):
        result = fodp_slide_titles(self.TITLED_XML)
        assert isinstance(result, list)

    def test_titled_entries_are_strings(self):
        result = fodp_slide_titles(self.TITLED_XML)
        for title in result:
            assert title is None or isinstance(title, str)
