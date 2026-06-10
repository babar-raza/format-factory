"""Tests for FODG get_shapes().

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-2-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import create_fodg, write_fodg, get_shapes, load


MINIMAL_FODG = b"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">
  <office:body>
    <office:drawing>
      <draw:page draw:name="Page1">
        <draw:text-box svg:x="1cm" svg:y="1cm" svg:width="10cm" svg:height="2cm">
          <text:p>Hello</text:p>
        </draw:text-box>
        <draw:rect svg:x="1cm" svg:y="4cm" svg:width="5cm" svg:height="3cm"/>
      </draw:page>
      <draw:page draw:name="Page2">
        <draw:ellipse svg:x="2cm" svg:y="2cm" svg:width="4cm" svg:height="4cm"/>
      </draw:page>
    </office:drawing>
  </office:body>
</office:document>
"""


class TestGetShapes:
    def test_returns_list(self):
        result = get_shapes(MINIMAL_FODG)
        assert isinstance(result, list)

    def test_correct_count(self):
        result = get_shapes(MINIMAL_FODG)
        assert len(result) == 3  # text-box + rect on page1, ellipse on page2

    def test_shape_has_required_keys(self):
        result = get_shapes(MINIMAL_FODG)
        for shape in result:
            assert "page_name" in shape
            assert "page_index" in shape
            assert "shape_index" in shape
            assert "tag" in shape
            assert "text" in shape

    def test_page_names(self):
        result = get_shapes(MINIMAL_FODG)
        page_names = [s["page_name"] for s in result]
        assert "Page1" in page_names
        assert "Page2" in page_names

    def test_page_indices(self):
        result = get_shapes(MINIMAL_FODG)
        assert result[0]["page_index"] == 0
        assert result[1]["page_index"] == 0
        assert result[2]["page_index"] == 1

    def test_shape_indices_reset_per_page(self):
        result = get_shapes(MINIMAL_FODG)
        assert result[0]["shape_index"] == 0
        assert result[1]["shape_index"] == 1
        assert result[2]["shape_index"] == 0  # reset for page2

    def test_tag_names(self):
        result = get_shapes(MINIMAL_FODG)
        tags = [s["tag"] for s in result]
        assert "text-box" in tags
        assert "rect" in tags
        assert "ellipse" in tags

    def test_text_extracted_from_textbox(self):
        result = get_shapes(MINIMAL_FODG)
        textbox_shapes = [s for s in result if s["tag"] == "text-box"]
        assert len(textbox_shapes) == 1
        assert textbox_shapes[0]["text"] == "Hello"

    def test_empty_document_returns_empty(self):
        empty_fodg = b"""<?xml version="1.0" encoding="UTF-8"?>
<office:document
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  office:mimetype="application/vnd.oasis.opendocument.graphics-flat-xml">
  <office:body><office:drawing><draw:page draw:name="Empty"/></office:drawing></office:body>
</office:document>"""
        result = get_shapes(empty_fodg)
        assert result == []

    def test_roundtrip_shape_count(self, tmp_path):
        model = create_fodg([{"name": "P1", "texts": ["one", "two"]}])
        dest = tmp_path / "test.fodg"
        write_fodg(model, dest)
        result = get_shapes(dest)
        assert len(result) == 2

    def test_file_source(self, tmp_path):
        dest = tmp_path / "test.fodg"
        dest.write_bytes(MINIMAL_FODG)
        result = get_shapes(dest)
        assert len(result) == 3
